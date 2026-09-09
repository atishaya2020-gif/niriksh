import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import UniqueConstraint

from app.db.models import RawRecord
from app.services.ingestion import import_csv


class FakeQuery:
    def __init__(self, records):
        self.records = records
        self.criteria = {}

    def filter_by(self, **criteria):
        self.criteria.update(criteria)
        return self

    def first(self):
        return next(
            (
                record
                for record in self.records
                if all(getattr(record, key) == value for key, value in self.criteria.items())
            ),
            None,
        )


class FakeSession:
    def __init__(self):
        self.records = []

    def query(self, model):
        if model is not RawRecord:
            raise ValueError("Only RawRecord queries are supported")
        return FakeQuery(self.records)

    def add(self, record):
        if any(r.case_id == record.case_id and r.record_id == record.record_id for r in self.records):
            from sqlalchemy.exc import IntegrityError
            raise IntegrityError("Duplicate", None, None)
        self.records.append(record)

    def commit(self):
        pass

    def flush(self):
        pass

    def begin_nested(self):
        class DummyNested:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                return False
        return DummyNested()


class CaseFixture:
    def __init__(self, case_id):
        self.id = case_id


class IngestionCaseScopingTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeSession()
        self.case_one = CaseFixture(1)
        self.case_two = CaseFixture(2)
        self.fixture_path = self.create_fixture()

    def tearDown(self):
        Path(self.fixture_path).unlink(missing_ok=True)

    def create_fixture(self):
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        handle.write("record_id,category,incident_datetime\n")
        handle.write("REC-001,Cybercrime,2026-01-01 10:00\n")
        handle.close()
        return handle.name

    def import_for_case(self, case):
        with patch("app.services.ingestion.import_csv_batch"):
            summary = import_csv(self.db, case, self.fixture_path)
            return summary["records_imported"]

    def test_model_uses_case_scoped_unique_constraint(self):
        constraints = [constraint for constraint in RawRecord.__table__.constraints if isinstance(constraint, UniqueConstraint)]
        self.assertEqual(len(constraints), 1)
        self.assertEqual(tuple(constraints[0].columns.keys()), ("case_id", "record_id"))

    def test_same_record_id_is_allowed_in_different_cases(self):
        self.assertEqual(self.import_for_case(self.case_one), 1)
        self.assertEqual(self.import_for_case(self.case_two), 1)
        self.assertEqual(len(self.db.records), 2)

    def test_same_record_id_is_skipped_in_the_same_case(self):
        self.assertEqual(self.import_for_case(self.case_one), 1)
        self.assertEqual(self.import_for_case(self.case_one), 0)
        self.assertEqual(len(self.db.records), 1)

    def test_reupload_to_same_case_is_idempotent(self):
        self.assertEqual(self.import_for_case(self.case_two), 1)
        self.assertEqual(self.import_for_case(self.case_two), 0)
        self.assertEqual(len(self.db.records), 1)


if __name__ == "__main__":
    unittest.main()
