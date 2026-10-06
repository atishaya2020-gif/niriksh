import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

from app.db.models import Base, User, Case, RawRecord, Alert
from app.api.dashboard import dashboard
from fastapi import HTTPException

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)

class TestDashboardAuthorization(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Setup data
        self.case1 = Case(case_number="c1", title="c1")
        self.case2 = Case(case_number="c2", title="c2")
        self.db.add_all([self.case1, self.case2])
        self.db.commit()

        self.rec1 = RawRecord(record_id="r1", case_id=self.case1.id, category="c", payload={})
        self.rec2 = RawRecord(record_id="r2", case_id=self.case2.id, category="c", payload={})
        self.db.add_all([self.rec1, self.rec2])

        self.alert1 = Alert(alert_type="t1", risk_level="H", reason="r", status="NEW")
        self.db.add(self.alert1)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    @patch("app.api.dashboard.neo4j_client.execute")
    def test_super_admin_gets_global_metrics(self, mock_neo4j):
        mock_neo4j.side_effect = [[{"count": 10}], [{"count": 20}], [{"count": 5}]]

        user = User(username="admin", password_hash="h", role="SUPER_ADMIN")
        res = dashboard(db=self.db, user=user)

        metrics = res["data"]["metrics"]
        self.assertEqual(metrics["total_cases"], 2)
        self.assertEqual(metrics["total_records"], 2)
        self.assertEqual(metrics["active_alerts"], 1)
        self.assertEqual(metrics["total_entities"], 10)
        self.assertEqual(metrics["detected_relationships"], 20)
        self.assertEqual(metrics["high_risk_entities"], 5)

        # Super admin does not pass authorized_case_ids
        for call in mock_neo4j.call_args_list:
            self.assertNotIn("authorized_case_ids", call.kwargs)

    @patch("app.api.dashboard.neo4j_client.execute")
    @patch("app.api.dashboard.get_authorized_case_ids")
    def test_normal_user_empty_scope(self, mock_auth_ids, mock_neo4j):
        mock_auth_ids.return_value = set()
        user = User(username="u1", password_hash="h", role="INVESTIGATOR")

        res = dashboard(db=self.db, user=user)

        metrics = res["data"]["metrics"]
        self.assertEqual(metrics["total_cases"], 0)
        self.assertEqual(metrics["total_records"], 0)
        self.assertEqual(metrics["active_alerts"], 0)
        self.assertEqual(metrics["total_entities"], 0)
        self.assertEqual(metrics["detected_relationships"], 0)
        self.assertEqual(metrics["high_risk_entities"], 0)

        mock_neo4j.assert_not_called()

    @patch("app.api.dashboard.neo4j_client.execute")
    @patch("app.api.dashboard.get_authorized_case_ids")
    def test_normal_user_authorized_scope(self, mock_auth_ids, mock_neo4j):
        mock_auth_ids.return_value = {self.case1.id}
        mock_neo4j.side_effect = [[{"count": 3}], [{"count": 4}], [{"count": 1}]]

        user = User(username="u1", password_hash="h", role="INVESTIGATOR")
        res = dashboard(db=self.db, user=user)

        metrics = res["data"]["metrics"]
        self.assertEqual(metrics["total_cases"], 1)
        self.assertEqual(metrics["total_records"], 1)
        self.assertEqual(metrics["active_alerts"], 0)  # alerts fail closed for normal users
        self.assertEqual(metrics["total_entities"], 3)
        self.assertEqual(metrics["detected_relationships"], 4)
        self.assertEqual(metrics["high_risk_entities"], 1)

        # Verify neo4j received authorized_case_ids=...
        self.assertEqual(mock_neo4j.call_count, 3)
        for call in mock_neo4j.call_args_list:
            self.assertEqual(call.kwargs.get("authorized_case_ids"), [self.case1.id])
            query = call.args[0]
            if "DISTINCT n" in query:
                self.assertIn("MATCH (n)-[r]-(m)", query)
            if "degree >=" in query:
                self.assertIn("MATCH (n)-[r]-(m)", query)

    @patch("app.api.dashboard.neo4j_client.execute")
    @patch("app.api.dashboard.get_authorized_case_ids")
    def test_response_shape_unchanged(self, mock_auth_ids, mock_neo4j):
        mock_auth_ids.return_value = {self.case1.id}
        mock_neo4j.side_effect = [[{"count": 3}], [{"count": 4}], [{"count": 1}]]
        user = User(username="u1", password_hash="h", role="SUPER_ADMIN")

        res = dashboard(db=self.db, user=user)

        self.assertIn("success", res)
        self.assertIn("data", res)
        self.assertIn("metrics", res["data"])
        self.assertIn("status", res["data"])
        self.assertIn("risk_note", res["data"])
        self.assertIn("message", res)

if __name__ == "__main__":
    unittest.main()
