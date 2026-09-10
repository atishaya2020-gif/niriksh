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
    created_at = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    records = []


class FakeCase2:
    id = 2
    case_number = "DEMO-SIH-002"
    title = "Second Case"
    description = "Another case"
    created_at = datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc)
    records = []


class FakeRawRecord:
    def __init__(self, record_id, case_id, category, incident_datetime, payload=None, created_at=None):
        self.id = hash(record_id) % 10000
        self.record_id = record_id
        self.case_id = case_id
        self.category = category
        self.incident_datetime = incident_datetime
        self.payload = payload or {}
        self.created_at = created_at or incident_datetime


class FakeAlert:
    def __init__(self, alert_id, case_id, entity_id, created_at, alert_type="HIGH_RISK_ENTITY", risk_level="HIGH"):
        self.id = alert_id
        self.case_id = case_id
        self.entity_id = entity_id
        self.alert_type = alert_type
        self.risk_level = risk_level
        self.risk_score = 70
        self.reason = "Test reason"
        self.confidence = 0.8
        self.status = "NEW"
        self.assigned_to = None
        self.created_at = created_at


class FakeEvidence:
    def __init__(self, ev_id, case_id, record_id, evidence_type, created_at, verified_at=None, verification_status="PENDING"):
        self.id = ev_id
        self.case_id = case_id
        self.record_id = record_id
        self.evidence_type = evidence_type
        self.source = "Test Source"
        self.description = "Test description"
        self.collection_timestamp = created_at
        self.verification_status = verification_status
        self.confidence = 0.8
        self.evidence_metadata = None
        self.verified_by = 1 if verified_at else None
        self.verified_at = verified_at
        self.created_at = created_at
        self.updated_at = created_at


CASE_1_RECORDS = [
    FakeRawRecord("REC-001", 1, "Call Data Record", datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)),
    FakeRawRecord("REC-002", 1, "Online Bank Transaction", datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)),
    FakeRawRecord("REC-003", 1, "Online FIR", datetime(2026, 1, 3, 8, 0, tzinfo=timezone.utc)),
]

CASE_2_RECORDS = [
    FakeRawRecord("REC-010", 2, "Call Data Record", datetime(2026, 2, 5, 10, 0, tzinfo=timezone.utc)),
]

CASE_1_ALERTS = [
    FakeAlert(1, 1, "person:test", datetime(2026, 1, 12, 14, 0, tzinfo=timezone.utc)),
]

CASE_1_EVIDENCE = [
    FakeEvidence(
        1, 1, "REC-001", "CALL_RECORD",
        datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        verified_at=datetime(2026, 1, 16, 9, 0, tzinfo=timezone.utc),
        verification_status="VERIFIED",
    ),
]


class FakeTimelineQuery:
    def __init__(self, model, case_id, items):
        self._model = model
        self._case_id = case_id
        self._items = items
        self._has_isnot_filter = False

    def filter(self, *args):
        return self

    def all(self):
        return self._items


class FakeTimelineDB:
    def __init__(self, target_case_id):
        self.target_case_id = target_case_id

    def get(self, model, pk):
        if model.__tablename__ == "cases":
            if pk == 1:
                return FakeCase()
            elif pk == 2:
                return FakeCase2()
            return None
        return None

    def query(self, model):
        tname = model.__tablename__
        if tname == "raw_records":
            items = [r for r in CASE_1_RECORDS + CASE_2_RECORDS if r.case_id == self.target_case_id]
            return _FakeChainQuery(items)
        if tname == "alerts":
            items = [a for a in CASE_1_ALERTS if a.case_id == self.target_case_id]
            return _FakeChainQuery(items)
        if tname == "evidence":
            items = [e for e in CASE_1_EVIDENCE if e.case_id == self.target_case_id]
            return _FakeChainQuery(items)
        return _FakeChainQuery([])


class _FakeChainQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *args):
        return self

    def all(self):
        return self._items

    def count(self):
        return len(self._items)

    def order_by(self, *args):
        return self

    def offset(self, val):
        return self

    def limit(self, val):
        return self


class TimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_returns_events(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_includes_case_created(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        event_types = [e["event_type"] for e in data["items"]]
        self.assertIn("CASE_CREATED", event_types)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_includes_record_events(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        record_events = [e for e in data["items"] if e["event_type"].startswith("RECORD_")]
        self.assertEqual(len(record_events), 3)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_includes_alert_events(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        alert_events = [e for e in data["items"] if e["event_type"] == "ALERT_GENERATED"]
        self.assertEqual(len(alert_events), 1)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_includes_evidence_events(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        evidence_events = [e for e in data["items"] if e["event_type"] in ("EVIDENCE_COLLECTED", "EVIDENCE_VERIFIED")]
        self.assertEqual(len(evidence_events), 2)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_is_ordered_chronologically(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        timestamps = [e["timestamp"] for e in data["items"]]
        self.assertEqual(timestamps, sorted(timestamps))

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_case_scoping(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(2)

        response = self.client.get(
            "/api/cases/2/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        for event in data["items"]:
            self.assertEqual(event["case_id"], 2)

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_case_not_found(self, mock_get_db, _neo4j):
        db = FakeTimelineDB(999)
        db.get = lambda model, pk: None
        mock_get_db.return_value = db

        response = self.client.get(
            "/api/cases/999/timeline",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_timeline_unauthorized(self):
        response = self.client.get("/api/cases/1/timeline")
        self.assertIn(response.status_code, (401, 403))

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_timeline_pagination(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline?page=1&page_size=2",
            headers=self.auth_headers,
        )
        data = response.json()
        self.assertLessEqual(len(data["items"]), 2)
        self.assertIn("total", data)
        self.assertGreater(data["total"], 2)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 2)


class TimelineEventFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @patch("app.api.cases.neo4j_client.execute", return_value=[])
    @patch("app.api.cases.get_db")
    def test_event_has_required_fields(self, mock_get_db, _neo4j):
        mock_get_db.return_value = FakeTimelineDB(1)

        response = self.client.get(
            "/api/cases/1/timeline",
            headers=self.auth_headers,
        )
        data = response.json()
        required_fields = {"timestamp", "event_type", "description", "case_id", "record_id", "entity_id", "source"}

        for event in data["items"]:
            self.assertTrue(
                required_fields.issubset(event.keys()),
                f"Missing fields in event: {required_fields - event.keys()}",
            )


if __name__ == "__main__":
    unittest.main()
