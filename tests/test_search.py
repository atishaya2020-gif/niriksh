import unittest
from unittest.mock import patch
from starlette.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.db.models import User, Case


class DummyUser:
    id = 1
    username = "test_investigator"
    role = "investigator"
    is_active = True


class SearchEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.token = create_access_token(DummyUser())
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get("/api/search?q=naveen")
        self.assertIn(response.status_code, (401, 403))

    def test_short_query_returns_422(self):
        response = self.client.get("/api/search?q=a", headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)

    def test_whitespace_only_short_query_returns_422(self):
        response = self.client.get("/api/search?q=   b   ", headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)

    def test_limit_validation(self):
        # limit < 1
        res_low = self.client.get("/api/search?q=naveen&limit=0", headers=self.auth_headers)
        self.assertEqual(res_low.status_code, 422)

        # limit > 50
        res_high = self.client.get("/api/search?q=naveen&limit=100", headers=self.auth_headers)
        self.assertEqual(res_high.status_code, 422)

    def test_person_partial_search_and_risk_scoring(self):
        mock_neo4j_data = [
            {
                "entity_id": "person:naveen agarwal",
                "entity_type": "Person",
                "default_label": "Naveen Agarwal",
                "properties": {"name": "Naveen Agarwal"},
                "case_ids": [1, 2],
                "record_count": 2,
            }
        ]
        mock_risk = {
            "risk_score": 57,
            "risk_level": "MEDIUM",
            "reasons": ["Associated with records across two cases"],
            "confidence": 0.82,
            "requires_human_verification": True,
            "analysis_type": "Simulated analytical output",
        }

        with patch("app.api.search.neo4j_client.execute", return_value=mock_neo4j_data), \
             patch("app.api.search.calculate_entity_risk", return_value=mock_risk):
            response = self.client.get("/api/search?q=naveen", headers=self.auth_headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["query"], "naveen")
            self.assertGreaterEqual(data["count"], 1)
            
            # Find the person item
            person_item = next((item for item in data["results"] if item["entity_id"] == "person:naveen agarwal"), None)
            self.assertIsNotNone(person_item)
            self.assertEqual(person_item["entity_type"], "Person")
            self.assertEqual(person_item["label"], "Naveen Agarwal")
            self.assertEqual(person_item["risk"], "MEDIUM")
            self.assertEqual(person_item["risk_score"], 57)
            self.assertEqual(person_item["case_ids"], [1, 2])
            self.assertTrue(person_item["cross_case"])
            self.assertEqual(person_item["record_count"], 2)

    def test_case_search_postgres(self):
        with patch("app.api.search.neo4j_client.execute", return_value=[]):
            response = self.client.get("/api/search?q=DEMO-SIH", headers=self.auth_headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertGreaterEqual(data["count"], 1)

            case_item = next((item for item in data["results"] if item["entity_type"] == "Case"), None)
            self.assertIsNotNone(case_item)
            self.assertTrue(case_item["entity_id"].startswith("case:"))
            self.assertIn("DEMO-SIH", case_item["label"])
            self.assertIsNone(case_item["risk"])
            self.assertIsNone(case_item["risk_score"])
            self.assertFalse(case_item["cross_case"])


if __name__ == "__main__":
    unittest.main()
