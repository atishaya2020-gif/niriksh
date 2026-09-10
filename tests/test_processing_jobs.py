import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.db.models import PROCESSING_STATUSES, ProcessingJob
from app.services.ingestion import import_csv
from app.services.processing_jobs import retry_job_graph, sync_job_graph, update_job


SENTINEL_CASE_ID = 987654321


class FakeQuery:
    def __init__(self, records):
        self.records = records
        self.criteria = {}

    def filter_by(self, **criteria):
        self.criteria.update(criteria)
        return self

    def filter(self, *args):
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

    def all(self):
        if self.criteria:
            return [
                record
                for record in self.records
                if all(getattr(record, key) == value for key, value in self.criteria.items())
            ]
        return list(self.records)


class FakeSession:
    def __init__(self):
        self.records = []
        self.jobs = []

    def query(self, model):
        from app.db.models import RawRecord

        if model is RawRecord:
            return FakeQuery(self.records)
        if model is ProcessingJob:
            return FakeQuery(self.jobs)
        raise ValueError(f"Unsupported query model: {model}")

    def add(self, record):
        from sqlalchemy.exc import IntegrityError
        from app.db.models import RawRecord

        if isinstance(record, RawRecord) and any(
            existing.case_id == record.case_id and existing.record_id == record.record_id
            for existing in self.records
        ):
            raise IntegrityError("Duplicate", None, None)
        if isinstance(record, RawRecord):
            self.records.append(record)
        elif isinstance(record, ProcessingJob):
            record.id = len(self.jobs) + 1
            self.jobs.append(record)

    def commit(self):
        pass

    def flush(self):
        pass

    def refresh(self, record):
        pass

    def begin_nested(self):
        class DummyNested:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, _exc_tb):
                return False

        return DummyNested()


class CaseFixture:
    def __init__(self, case_id):
        self.id = case_id


class ProcessingJobTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeSession()
        self.case = CaseFixture(SENTINEL_CASE_ID)
        self.fixture_path = self.create_fixture()

    def tearDown(self):
        Path(self.fixture_path).unlink(missing_ok=True)

    def create_fixture(self):
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        handle.write("record_id,category,incident_datetime,person_name,city\n")
        handle.write("REC-SENTINEL-001,Cybercrime,2026-01-01 10:00,Test Person,Delhi\n")
        handle.close()
        return handle.name

    def make_job(self, **kwargs):
        values = dict(
            id=1,
            case_id=SENTINEL_CASE_ID,
            uploader_id=1,
            status="RECEIVED",
            stage="RECEIVED",
            source_filename="sentinel.csv",
            source_sha256="abc123",
            source_size_bytes=12,
            record_ids=[],
            records_received=0,
            records_processed=0,
            entities_extracted=0,
            relationships_detected=0,
            matches_found=0,
            alerts_generated=0,
            attempt_count=0,
            error_message=None,
            created_at=None,
            started_at=None,
            completed_at=None,
        )
        values.update(kwargs)
        job = ProcessingJob()
        for key, value in values.items():
            setattr(job, key, value)
        self.db.jobs.append(job)
        return job

    def test_processing_statuses_are_defined(self):
        self.assertIn("RECEIVED", PROCESSING_STATUSES)
        self.assertIn("GRAPH_PENDING", PROCESSING_STATUSES)
        self.assertIn("COMPLETED", PROCESSING_STATUSES)
        self.assertIn("FAILED", PROCESSING_STATUSES)

    def test_source_hash_is_sha256(self):
        contents = Path(self.fixture_path).read_bytes()
        digest = hashlib.sha256(contents).hexdigest()
        self.assertEqual(len(digest), 64)

    def test_job_state_transitions_and_extraction_counters(self):
        job = self.make_job()
        with patch("app.services.processing_jobs.import_csv_batch") as mock_batch:
            mock_batch.return_value = {"entities_extracted": 3, "relationships_detected": 2, "records_projected": 1}
            result = import_csv(self.db, self.case, self.fixture_path, job=job)
        self.assertEqual(result["records_imported"], 1)
        self.assertEqual(job.status, "COMPLETED")
        self.assertEqual(job.stage, "COMPLETED")
        self.assertEqual(job.entities_extracted, 3)
        self.assertEqual(job.relationships_detected, 2)
        self.assertEqual(job.attempt_count, 1)
        self.assertEqual(job.record_ids, ["REC-SENTINEL-001"])
        mock_batch.assert_called_once()

    def test_duplicate_raw_record_is_skipped_and_job_can_retry_graph(self):
        job = self.make_job()
        with patch("app.services.processing_jobs.import_csv_batch") as mock_batch:
            mock_batch.side_effect = RuntimeError("neo4j unavailable")
            first = import_csv(self.db, self.case, self.fixture_path, job=job)
        self.assertEqual(first["records_imported"], 1)
        self.assertEqual(job.status, "FAILED")
        self.assertEqual(len(self.db.records), 1)

        with patch("app.services.processing_jobs.import_csv_batch") as mock_batch:
            mock_batch.return_value = {"entities_extracted": 3, "relationships_detected": 2, "records_projected": 1}
            second = import_csv(self.db, self.case, self.fixture_path, job=job)
        self.assertEqual(second["records_imported"], 0)
        self.assertEqual(len(self.db.records), 1)
        self.assertEqual(job.status, "COMPLETED")
        mock_batch.assert_called_once()

    def test_retry_job_graph_uses_stored_record_ids(self):
        job = self.make_job(status="FAILED", record_ids=["REC-SENTINEL-001"], error_message="Graph: boom")
        from app.db.models import RawRecord

        self.db.records.append(
            RawRecord(
                record_id="REC-SENTINEL-001",
                case_id=SENTINEL_CASE_ID,
                category="Cybercrime",
                payload={"record_id": "REC-SENTINEL-001", "category": "Cybercrime"},
            )
        )
        with patch("app.services.processing_jobs.import_csv_batch") as mock_batch:
            mock_batch.return_value = {"entities_extracted": 4, "relationships_detected": 5, "records_projected": 1}
            result = retry_job_graph(self.db, job)
        self.assertTrue(result["success"])
        self.assertEqual(job.status, "COMPLETED")
        self.assertEqual(job.entities_extracted, 4)
        mock_batch.assert_called_once()
        self.assertEqual(mock_batch.call_args[0][1], SENTINEL_CASE_ID)

    def test_retry_rejected_from_completed(self):
        job = self.make_job(status="COMPLETED")
        result = retry_job_graph(self.db, job)
        self.assertFalse(result["success"])

    def test_update_job_sets_stage(self):
        job = self.make_job()
        update_job(self.db, job, "GRAPH_PENDING")
        self.assertEqual(job.status, "GRAPH_PENDING")
        self.assertEqual(job.stage, "GRAPH_PENDING")
        self.assertIsNotNone(job.started_at)


class GraphIdempotencyTests(unittest.TestCase):
    def test_repeated_projection_uses_merge_and_counts_unique_entities(self):
        from app.services.graph_service import import_csv_batch

        row = {
            "record_id": "REC-SENTINEL-002",
            "category": "Cybercrime",
            "person_name": "Test Person",
            "city": "Delhi",
        }
        with patch("app.services.graph_service.neo4j_client.execute_write_batch") as mock_execute:
            first = import_csv_batch([row], SENTINEL_CASE_ID)
            second = import_csv_batch([row], SENTINEL_CASE_ID)
        self.assertEqual(first["entities_extracted"], second["entities_extracted"])
        self.assertGreater(first["entities_extracted"], 0)
        self.assertGreater(first["relationships_detected"], 0)
        cypher = "\n".join(call[0][0] for call in mock_execute.call_args_list)
        self.assertIn("MERGE (n:", cypher)
        self.assertIn("evidence_record_ids", cypher)


if __name__ == "__main__":
    unittest.main()
