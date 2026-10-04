import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, User, Case, Jurisdiction, UserJurisdiction, CaseJurisdiction, CaseGrant, CrossStateGrant, AuditEvent, CAPABILITIES, SAFE_CROSS_STATE_CAPABILITIES

# Compile JSONB as JSON for SQLite tests
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)

class TestAuthorizationFoundation(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.u1 = User(username="u1", password_hash="h", role="investigator")
        self.u2 = User(username="u2", password_hash="h", role="investigator")
        self.c1 = Case(case_number="c1", title="c1")
        self.j1 = Jurisdiction(name="j1", code="J1")
        self.session.add_all([self.u1, self.u2, self.c1, self.j1])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_capability_constants(self):
        self.assertIn("case:view", CAPABILITIES)
        self.assertIn("case:create", CAPABILITIES)
        self.assertNotIn("cross_case:correlate", SAFE_CROSS_STATE_CAPABILITIES)
        self.assertTrue(all(c in CAPABILITIES for c in SAFE_CROSS_STATE_CAPABILITIES))

    def test_jurisdiction_creation(self):
        j = Jurisdiction(name="j2", code="J2")
        self.session.add(j)
        self.session.commit()
        self.assertIsNotNone(j.id)

    def test_user_jurisdiction_relationship(self):
        uj = UserJurisdiction(user_id=self.u1.id, jurisdiction_id=self.j1.id)
        self.session.add(uj)
        self.session.commit()
        self.assertEqual(uj.user_id, self.u1.id)

    def test_case_jurisdiction_relationship(self):
        cj = CaseJurisdiction(case_id=self.c1.id, jurisdiction_id=self.j1.id)
        self.session.add(cj)
        self.session.commit()
        self.assertEqual(cj.case_id, self.c1.id)

    def test_case_grant_stores_one_capability(self):
        g = CaseGrant(user_id=self.u1.id, case_id=self.c1.id, capability="case:view", granted_by=self.u1.id)
        self.session.add(g)
        self.session.commit()
        self.assertEqual(g.capability, "case:view")

    def test_active_duplicate_grant_rejected(self):
        g1 = CaseGrant(user_id=self.u1.id, case_id=self.c1.id, capability="case:view", granted_by=self.u1.id)
        g2 = CaseGrant(user_id=self.u1.id, case_id=self.c1.id, capability="case:view", granted_by=self.u1.id)
        self.session.add(g1)
        self.session.commit()
        self.session.add(g2)
        with self.assertRaises(Exception):
            self.session.commit()

    def test_revoked_historical_grant_coexists(self):
        g1 = CaseGrant(user_id=self.u1.id, case_id=self.c1.id, capability="case:view", granted_by=self.u1.id, revoked_at=datetime.now(timezone.utc))
        g2 = CaseGrant(user_id=self.u1.id, case_id=self.c1.id, capability="case:view", granted_by=self.u1.id)
        self.session.add_all([g1, g2])
        self.session.commit()
        self.assertEqual(self.session.query(CaseGrant).count(), 2)

    def test_cross_state_grant_persistence(self):
        csg = CrossStateGrant(requesting_user_id=self.u1.id, target_jurisdiction_id=self.j1.id, capability="case:view", justification="test")
        self.session.add(csg)
        self.session.commit()
        self.assertEqual(csg.capability, "case:view")

    def test_audit_event_persistence(self):
        ae = AuditEvent(event_type="test", outcome="SUCCESS", metadata_json={"foo": "bar"})
        self.session.add(ae)
        self.session.commit()
        self.assertEqual(ae.metadata_json["foo"], "bar")

    def test_user_case_compatibility(self):
        u = User(username="u3", password_hash="h")
        c = Case(case_number="c2", title="c2")
        self.session.add_all([u, c])
        self.session.commit()
        self.assertIsNotNone(u.id)
        self.assertIsNotNone(c.id)
