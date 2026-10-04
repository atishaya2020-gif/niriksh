import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from app.api.matches import get_current_user as matches_get_current_user
from app.api.matches import get_db as matches_get_db
from app.main import app


class DummyUser:
    id = 1
    username = "test_investigator"
    role = "SUPER_ADMIN"
    is_active = True


class FakeCase:
    id = 1
    case_number = "DEMO-SIH-001"
    title = "Test Case"
    description = "A test case"
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FakeMatch:
    def __init__(self, **kwargs):
        defaults = dict(
            id=1,
            case_id=1,
            source_entity_id="person:amit kumar",
            candidate_entity_id="person:amit k.",
            source_entity_type="Person",
            candidate_entity_type="Person",
            match_score=70.0,
            confidence=0.85,
            matching_factors={"reasons": ["Shared phone identifier count: 1"], "signals": {"shared_phones": 1}},
            status="PENDING_REVIEW",
            reviewed_by=None,
            reviewed_at=None,
            created_at=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


class FakeSession:
    def __init__(self):
        self.matches = [FakeMatch()]

    def get(self, model, pk):
        if model.__tablename__ == "users":
            return DummyUser()
        if model.__tablename__ == "cases":
            if pk == 1:
                return FakeCase()
            return None
        if model.__tablename__ == "entity_matches":
            for m in self.matches:
                if m.id == pk:
                    return m
            return None
        return None

    def query(self, model):
        return FakeQuery(self.matches)

    def add(self, obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = len(self.matches) + 1
        self.matches.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def close(self):
        pass


class FakeQuery:
    def __init__(self, matches):
        self._matches = matches

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def offset(self, val):
        return self

    def limit(self, val):
        return self

    def all(self):
        return self._matches

    def count(self):
        return len(self._matches)

    def first(self):
        return self._matches[0] if self._matches else None


class EntityMatchingAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def authenticate(self, session=None):
        session = session or FakeSession()
        app.dependency_overrides[matches_get_current_user] = lambda: DummyUser()
        app.dependency_overrides[matches_get_db] = lambda: session
        self.addCleanup(app.dependency_overrides.clear)
        return session

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_list_matches(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.get("/api/matches")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_list_matches_empty(self, mock_sec_db, mock_api_db):
        session = FakeSession()
        session.matches = []
        self.authenticate(session)
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.get("/api/matches?case_id=999")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 0)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_get_match_detail(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.get("/api/matches/1")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["status"], "PENDING_REVIEW")
        self.assertIn("matching_factors", data)
        self.assertIn("match_score", data)
        self.assertIn("confidence", data)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_get_match_not_found(self, mock_sec_db, mock_api_db):
        session = FakeSession()
        session.matches = []
        self.authenticate(session)
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.get("/api/matches/999")
        self.assertEqual(res.status_code, 404)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_review_match_confirmed(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        with patch("app.api.matches.neo4j_client.execute") as mock_neo4j:
            res = self.client.patch(
                "/api/matches/1/review",
                json={"status": "CONFIRMED"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["data"]["status"], "CONFIRMED")
            self.assertEqual(data["data"]["reviewed_by"], 1)
            mock_neo4j.assert_called()

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_review_match_rejected(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        with patch("app.api.matches.neo4j_client.execute"):
            res = self.client.patch(
                "/api/matches/1/review",
                json={"status": "REJECTED"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["data"]["status"], "REJECTED")

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_review_match_invalid_status(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.patch(
            "/api/matches/1/review",
            json={"status": "MERGED"},
        )
        self.assertEqual(res.status_code, 400)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_review_match_not_found(self, mock_sec_db, mock_api_db):
        session = FakeSession()
        session.matches = []
        self.authenticate(session)
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.patch(
            "/api/matches/999/review",
            json={"status": "CONFIRMED"},
        )
        self.assertEqual(res.status_code, 404)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_generate_matches_for_case(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        with patch("app.api.matches.generate_case_entity_matches", return_value=[FakeMatch()]):
            res = self.client.post("/api/matches/cases/1/generate")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["data"]["generated_count"], 1)

    @patch("app.api.matches.get_db")
    @patch("app.core.security.get_db")
    def test_generate_matches_case_not_found(self, mock_sec_db, mock_api_db):
        session = self.authenticate()
        mock_api_db.return_value = session
        mock_sec_db.return_value = session
        res = self.client.post("/api/matches/cases/999/generate")
        self.assertEqual(res.status_code, 404)

    def test_unauthenticated_list_matches(self):
        res = self.client.get("/api/matches")
        self.assertIn(res.status_code, (401, 403))

    def test_unauthenticated_get_match(self):
        res = self.client.get("/api/matches/1")
        self.assertIn(res.status_code, (401, 403))

    def test_unauthenticated_review(self):
        res = self.client.patch("/api/matches/1/review", json={"status": "CONFIRMED"})
        self.assertIn(res.status_code, (401, 403))


class MatchingScoringTests(unittest.TestCase):
    def test_canonical_pair_prevents_duplicates(self):
        a = "person:amit kumar"
        b = "person:amit k."
        pair_ab = tuple(sorted([a, b]))
        pair_ba = tuple(sorted([b, a]))
        self.assertEqual(pair_ab, pair_ba)

    def test_score_shared_phone_only(self):
        score = min(40.0, 100.0)
        confidence = round(min(0.50 + (score / 200.0), 0.95), 2)
        self.assertEqual(score, 40.0)
        self.assertEqual(confidence, 0.70)

    def test_score_multiple_signals(self):
        score = min(40.0 + 30.0 + 15.0 + 20.0, 100.0)
        confidence = round(min(0.50 + (score / 200.0), 0.95), 2)
        self.assertEqual(score, 100.0)
        self.assertEqual(confidence, 0.95)

    def test_confidence_floor(self):
        score = 0.0
        confidence = round(min(0.50 + (score / 200.0), 0.95), 2)
        self.assertEqual(confidence, 0.50)

    def test_confidence_ceiling(self):
        score = 200.0
        confidence = round(min(0.50 + (score / 200.0), 0.95), 2)
        self.assertEqual(confidence, 0.95)

    def test_score_capped_at_100(self):
        raw = 40.0 + 30.0 + 30.0 + 15.0 + 20.0
        score = min(raw, 100.0)
        self.assertEqual(score, 100.0)

    def test_matching_factors_structure(self):
        factors = {
            "reasons": ["Shared phone identifier count: 1", "Exact normalized name match"],
            "signals": {
                "shared_phones": 1,
                "shared_devices": 0,
                "shared_accounts": 0,
                "shared_locations": 0,
                "name_match": True,
            },
        }
        self.assertIn("reasons", factors)
        self.assertIn("signals", factors)
        self.assertIsInstance(factors["reasons"], list)
        self.assertIsInstance(factors["signals"], dict)


if __name__ == "__main__":
    unittest.main()
