import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

patch("app.main.Base.metadata.create_all").start()
patch("app.db.postgres.engine").start()
patch("app.main.auth.seed_admin").start()

from starlette.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


class DummyUser:
    id = 1
    username = "test_investigator"
    role = "investigator"
    is_active = True


class FakeCase:
    id = 1
    case_number = "DEMO-SIH-001"
    title = "Test Case"
    description = "A test case"
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    records = []


class FakeEvidence:
    def __init__(self, **kwargs):
        defaults = dict(
            id=1,
            case_id=1,
            record_id="REC-001",
            evidence_type="CALL_RECORD",
            source="CDR Dataset",
            description="Call record between two subjects",
            collection_timestamp=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
            verification_status="PENDING",
            confidence=0.85,
            evidence_metadata={"duration_sec": "120"},
            verified_by=None,
            verified_at=None,
            created_at=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
        )
        defaults.update(kwargs)
        for key, value in defaults.items():
            setattr(self, key, value)


class FakeRecord:
    id = 1
    record_id = "REC-001"
    case_id = 1


class FakeSession:
    def __init__(self):
        self._added = []
        self._committed = False

    def get(self, model, pk):
        if model.__tablename__ == "cases":
            if pk == 1:
                return FakeCase()
            return None
        if model.__tablename__ == "evidence":
            if pk == 1:
                return FakeEvidence()
            return None
        return None

    def query(self, model):
        return FakeQuery(model)

    def add(self, obj):
        self._added.append(obj)

    def commit(self):
        self._committed = True

    def refresh(self, obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = 1


class FakeQuery:
    def __init__(self, model):
        self._model = model
        self._filters = []
        self._order = None
        self._offset_val = None
        self._limit_val = None
        self._count_val = 0

    def filter(self, *args):
        self._filters.extend(args)
        return self

    def first(self):
        if self._model.__tablename__ == "cases":
            return FakeCase()
        if self._model.__tablename__ == "evidence":
            return FakeEvidence()
        if self._model.__tablename__ == "raw_records":
            return FakeRecord()
        return None

    def all(self):
        if self._model.__tablename__ == "evidence":
            return [FakeEvidence(id=1), FakeEvidence(id=2, evidence_type="DOCUMENT")]
        if self._model.__tablename__ == "raw_records":
            return []
        if self._model.__tablename__ == "alerts":
            return []
        return []

    def count(self):
        return 2

    def order_by(self, *args):
        self._order = args
        return self

    def offset(self, val):
        self._offset_val = val
        return self

    def limit(self, val):
        self._limit_val = val
        return self


class EvidenceCreationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.evidence.get_db")
    def test_create_evidence_success(self, mock_get_db):
        mock_get_db.return_value = FakeSession()

        response = self.client.post(
            "/api/evidence/cases/1/evidence",
            headers=self.auth_headers,
            json={
                "evidence_type": "CALL_RECORD",
                "source": "CDR Dataset",
                "description": "Call record between two subjects",
                "confidence": 0.85,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["case_id"], 1)
        self.assertEqual(data["evidence_type"], "CALL_RECORD")
        self.assertEqual(data["verification_status"], "PENDING")

    @patch("app.api.evidence.get_db")
    def test_create_evidence_with_metadata(self, mock_get_db):
        mock_get_db.return_value = FakeSession()

        response = self.client.post(
            "/api/evidence/cases/1/evidence",
            headers=self.auth_headers,
            json={
                "evidence_type": "FINANCIAL_TRANSACTION",
                "source": "Bank Statement",
                "description": "Suspicious transfer",
                "confidence": 0.72,
                "evidence_metadata": {"amount": "50000", "currency": "INR"},
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["evidence_type"], "FINANCIAL_TRANSACTION")

    @patch("app.api.evidence.get_db")
    def test_create_evidence_invalid_type(self, mock_get_db):
        mock_get_db.return_value = FakeSession()

        response = self.client.post(
            "/api/evidence/cases/1/evidence",
            headers=self.auth_headers,
            json={
                "evidence_type": "INVALID_TYPE",
                "source": "Test",
                "description": "Bad type",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid evidence_type", response.json()["detail"])

    @patch("app.api.evidence.get_db")
    def test_create_evidence_case_not_found(self, mock_get_db):
        db = FakeSession()
        db.get = lambda model, pk: None
        mock_get_db.return_value = db

        response = self.client.post(
            "/api/evidence/cases/999/evidence",
            headers=self.auth_headers,
            json={
                "evidence_type": "CALL_RECORD",
                "source": "Test",
                "description": "No case",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Case not found")

    def test_create_evidence_unauthorized(self):
        response = self.client.post(
            "/api/evidence/cases/1/evidence",
            json={
                "evidence_type": "CALL_RECORD",
                "source": "Test",
                "description": "No auth",
            },
        )
        self.assertIn(response.status_code, (401, 403))


class EvidenceRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.evidence.get_db")
    def test_get_evidence_success(self, mock_get_db):
        mock_get_db.return_value = FakeSession()

        response = self.client.get(
            "/api/evidence/1",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertIn("evidence_type", data)

    @patch("app.api.evidence.get_db")
    def test_get_evidence_not_found(self, mock_get_db):
        db = FakeSession()
        db.get = lambda model, pk: None
        mock_get_db.return_value = db

        response = self.client.get(
            "/api/evidence/999",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_get_evidence_unauthorized(self):
        response = self.client.get("/api/evidence/1")
        self.assertIn(response.status_code, (401, 403))


class EvidenceListingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.evidence.get_db")
    def test_list_case_evidence(self, mock_get_db):
        mock_get_db.return_value = FakeSession()

        response = self.client.get(
            "/api/evidence/cases/1/evidence",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 50)

    @patch("app.api.evidence.get_db")
    def test_list_case_evidence_case_not_found(self, mock_get_db):
        db = FakeSession()
        db.get = lambda model, pk: None
        mock_get_db.return_value = db

        response = self.client.get(
            "/api/evidence/cases/999/evidence",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)


class EvidenceVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.evidence.get_db")
    def test_verify_evidence_success(self, mock_get_db):
        db = FakeSession()
        evidence = FakeEvidence()
        db.get = lambda model, pk: evidence if model.__tablename__ == "evidence" else None
        mock_get_db.return_value = db

        response = self.client.patch(
            "/api/evidence/1/verify",
            headers=self.auth_headers,
            json={"status": "VERIFIED"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["verification_status"], "VERIFIED")

    @patch("app.api.evidence.get_db")
    def test_verify_evidence_invalid_status(self, mock_get_db):
        db = FakeSession()
        evidence = FakeEvidence()
        db.get = lambda model, pk: evidence if model.__tablename__ == "evidence" else None
        mock_get_db.return_value = db

        response = self.client.patch(
            "/api/evidence/1/verify",
            headers=self.auth_headers,
            json={"status": "INVALID_STATUS"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status", response.json()["detail"])

    @patch("app.api.evidence.get_db")
    def test_verify_evidence_not_found(self, mock_get_db):
        db = FakeSession()
        db.get = lambda model, pk: None
        mock_get_db.return_value = db

        response = self.client.patch(
            "/api/evidence/999/verify",
            headers=self.auth_headers,
            json={"status": "VERIFIED"},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
