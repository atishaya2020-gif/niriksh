import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.core.security import create_access_token
from app.db.models import Base, Case, CaseGrant, User
from app.db.postgres import get_db
from app.main import app


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)


class SearchEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        app.dependency_overrides[get_db] = lambda: self.session
        self.client = TestClient(app)

        self.admin = User(username="admin", password_hash="h", role="ADMIN")
        self.user_a = User(username="user_a", password_hash="h", role="INVESTIGATOR")
        self.user_b = User(username="user_b", password_hash="h", role="INVESTIGATOR")
        self.super_admin = User(username="super_admin", password_hash="h", role="SUPER_ADMIN")
        self.session.add_all([self.admin, self.user_a, self.user_b, self.super_admin])
        self.session.commit()

        self.case_a = Case(case_number="DEMO-SIH-A", title="Case A")
        self.case_b = Case(case_number="DEMO-SIH-B", title="Case B")
        self.session.add_all([self.case_a, self.case_b])
        self.session.commit()

        self.session.add_all([
            CaseGrant(user_id=self.user_a.id, case_id=self.case_a.id, capability="search:view", granted_by=self.admin.id),
            CaseGrant(user_id=self.user_b.id, case_id=self.case_b.id, capability="search:view", granted_by=self.admin.id),
        ])
        self.session.commit()

        self.headers_a = {"Authorization": f"Bearer {create_access_token(self.user_a)}"}
        self.headers_b = {"Authorization": f"Bearer {create_access_token(self.user_b)}"}
        self.headers_super = {"Authorization": f"Bearer {create_access_token(self.super_admin)}"}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get("/api/search?q=naveen")
        self.assertIn(response.status_code, (401, 403))

    def test_short_query_returns_422(self):
        response = self.client.get("/api/search?q=a", headers=self.headers_a)
        self.assertEqual(response.status_code, 422)

    def test_whitespace_only_short_query_returns_422(self):
        response = self.client.get("/api/search?q=   b   ", headers=self.headers_a)
        self.assertEqual(response.status_code, 422)

    def test_limit_validation(self):
        res_low = self.client.get("/api/search?q=naveen&limit=0", headers=self.headers_a)
        self.assertEqual(res_low.status_code, 422)

        res_high = self.client.get("/api/search?q=naveen&limit=100", headers=self.headers_a)
        self.assertEqual(res_high.status_code, 422)

    def test_authorized_case_entity_search_is_scoped(self):
        mock_neo4j_data = [
            {
                "entity_id": "person:case-a-person",
                "entity_type": "Person",
                "default_label": "Case A Person",
                "properties": {"name": "Case A Person"},
                "case_ids": [self.case_a.id],
                "record_count": 1,
            }
        ]
        mock_risk = {"risk_score": 12, "risk_level": "LOW"}

        with patch("app.api.search.neo4j_client.execute", return_value=mock_neo4j_data) as mock_execute, \
             patch("app.api.search.calculate_entity_risk", return_value=mock_risk):
            response = self.client.get("/api/search?q=Case+A+Person", headers=self.headers_a)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["entity_id"], "person:case-a-person")
        self.assertEqual(data["results"][0]["case_ids"], [self.case_a.id])
        self.assertEqual(mock_execute.call_args.kwargs["authorized_case_ids"], [self.case_a.id])
        self.assertFalse(mock_execute.call_args.kwargs["is_super_admin"])

    def test_user_a_cannot_retrieve_case_b_case_metadata(self):
        with patch("app.api.search.neo4j_client.execute", return_value=[]):
            response = self.client.get("/api/search?q=DEMO-SIH-B", headers=self.headers_a)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], [])
        self.assertEqual(data["count"], 0)

    def test_postgres_case_search_respects_authorized_case_ids(self):
        with patch("app.api.search.neo4j_client.execute", return_value=[]):
            response = self.client.get("/api/search?q=DEMO-SIH", headers=self.headers_a)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        case_items = [item for item in data["results"] if item["entity_type"] == "Case"]
        self.assertEqual(len(case_items), 1)
        self.assertEqual(case_items[0]["case_ids"], [self.case_a.id])
        self.assertEqual(case_items[0]["label"], "DEMO-SIH-A")

    def test_empty_authorized_scope_returns_no_data(self):
        no_scope_user = User(username="no_scope", password_hash="h", role="INVESTIGATOR")
        self.session.add(no_scope_user)
        self.session.commit()
        headers = {"Authorization": f"Bearer {create_access_token(no_scope_user)}"}

        with patch("app.api.search.neo4j_client.execute") as mock_execute:
            response = self.client.get("/api/search?q=DEMO-SIH", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"query": "DEMO-SIH", "results": [], "count": 0})
        mock_execute.assert_not_called()

    def test_super_admin_retains_privileged_search(self):
        mock_neo4j_data = [
            {
                "entity_id": "person:case-b-person",
                "entity_type": "Person",
                "default_label": "Case B Person",
                "properties": {"name": "Case B Person"},
                "case_ids": [self.case_b.id],
                "record_count": 1,
            }
        ]

        with patch("app.api.search.neo4j_client.execute", return_value=mock_neo4j_data) as mock_execute, \
             patch("app.api.search.calculate_entity_risk", return_value={"risk_score": 0, "risk_level": "LOW"}):
            response = self.client.get("/api/search?q=Case+B+Person", headers=self.headers_super)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()["count"], 1)
        self.assertTrue(mock_execute.call_args.kwargs["is_super_admin"])

    def test_direct_entity_match_uses_provenance_filter(self):
        with patch("app.api.search.neo4j_client.execute", return_value=[]) as mock_execute:
            response = self.client.get("/api/search?q=phone:x", headers=self.headers_a)

        self.assertEqual(response.status_code, 200)
        cypher = mock_execute.call_args.args[0]
        self.assertIn("MATCH (n)-[r]-(rel_target)", cypher)
        self.assertIn("r.case_id IN $authorized_case_ids", cypher)
        self.assertIn("r.evidence_case_ids", cypher)
        self.assertEqual(mock_execute.call_args.kwargs["authorized_case_ids"], [self.case_a.id])

    def test_user_b_can_search_own_case(self):
        with patch("app.api.search.neo4j_client.execute", return_value=[]):
            response = self.client.get("/api/search?q=DEMO-SIH-B", headers=self.headers_b)

        self.assertEqual(response.status_code, 200)
        case_items = [item for item in response.json()["results"] if item["entity_type"] == "Case"]
        self.assertEqual(len(case_items), 1)
        self.assertEqual(case_items[0]["case_ids"], [self.case_b.id])


if __name__ == "__main__":
    unittest.main()
