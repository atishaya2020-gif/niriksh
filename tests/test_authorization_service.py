import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.db.models import Base, User, Case, CaseGrant, Jurisdiction, UserJurisdiction, CaseJurisdiction, CrossStateGrant, CAPABILITIES
from app.services.authorization import (
    build_authorized_scope, get_case_capabilities, has_case_capability,
    require_case_capability, get_authorized_case, has_global_capability
)

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)

class TestAuthorizationService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.u_admin = User(username="admin", password_hash="hash", role="ADMIN")
        self.u_investigator = User(username="inv1", password_hash="hash", role="INVESTIGATOR")
        self.u_viewer = User(username="view1", password_hash="hash", role="VIEWER")
        self.c1 = Case(case_number="c1", title="c1")
        self.j1 = Jurisdiction(name="j1", code="J1")

        self.session.add_all([self.u_admin, self.u_investigator, self.u_viewer, self.c1, self.j1])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_super_admin_privileged(self):
        u_super = User(username="super", password_hash="hash", role="SUPER_ADMIN")
        self.session.add(u_super)
        self.session.commit()
        self.assertTrue(has_case_capability(self.session, u_super, self.c1.id, "admin:manage_users"))

    def test_normal_role_ceiling(self):
        # Investigator should not have admin capabilities
        self.assertFalse(has_case_capability(self.session, self.u_investigator, self.c1.id, "admin:manage_users"))

    def test_jurisdiction_inheritance(self):
        # Setup: Investigator has j1, case has j1
        self.session.add(UserJurisdiction(user_id=self.u_investigator.id, jurisdiction_id=self.j1.id))
        self.session.add(CaseJurisdiction(case_id=self.c1.id, jurisdiction_id=self.j1.id))
        self.session.commit()

        # Inherited: case:view, search:view
        self.assertTrue(has_case_capability(self.session, self.u_investigator, self.c1.id, "case:view"))
        # Not inherited: evidence:create
        self.assertFalse(has_case_capability(self.session, self.u_investigator, self.c1.id, "evidence:create"))

    def test_explicit_case_grant_within_ceiling(self):
        # Investigator role has case:update. Grant should work.
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=self.c1.id, capability="case:update", granted_by=self.u_admin.id))
        self.session.commit()
        self.assertTrue(has_case_capability(self.session, self.u_investigator, self.c1.id, "case:update"))

    def test_explicit_case_grant_exceeds_ceiling(self):
        # Investigator role does NOT have admin:manage_users. Grant should be ignored (Intersection).
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=self.c1.id, capability="admin:manage_users", granted_by=self.u_admin.id))
        self.session.commit()
        self.assertFalse(has_case_capability(self.session, self.u_investigator, self.c1.id, "admin:manage_users"))

    def test_revoked_expired_grant(self):
        now = datetime.now(timezone.utc)
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=self.c1.id, capability="case:update", granted_by=self.u_admin.id, revoked_at=now))
        self.session.add(CaseGrant(user_id=self.u_viewer.id, case_id=self.c1.id, capability="case:view", granted_by=self.u_admin.id, expires_at=now - timedelta(days=1)))
        self.session.commit()

        self.assertFalse(has_case_capability(self.session, self.u_investigator, self.c1.id, "case:update"))
        self.assertFalse(has_case_capability(self.session, self.u_viewer, self.c1.id, "case:view"))

    def test_cross_state_access(self):
        # Setup: User has access to j1 (cross-state), case has j1
        self.session.add(CaseJurisdiction(case_id=self.c1.id, jurisdiction_id=self.j1.id))
        self.session.add(CrossStateGrant(requesting_user_id=self.u_investigator.id, target_jurisdiction_id=self.j1.id, capability="case:view", justification="test", status="APPROVED"))
        self.session.commit()

        self.assertTrue(has_case_capability(self.session, self.u_investigator, self.c1.id, "case:view"))
        self.assertFalse(has_case_capability(self.session, self.u_investigator, self.c1.id, "evidence:create"))

    def test_get_authorized_case(self):
        # Success
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=self.c1.id, capability="case:view", granted_by=self.u_admin.id))
        self.session.commit()
        case = get_authorized_case(self.session, self.u_investigator, self.c1.id, "case:view")
        self.assertEqual(case.id, self.c1.id)

        # 404
        with self.assertRaises(HTTPException) as cm:
            get_authorized_case(self.session, self.u_investigator, 999, "case:view")
        self.assertEqual(cm.exception.status_code, 404)

        # 404 (cannot view case -> hidden)
        with self.assertRaises(HTTPException) as cm:
            get_authorized_case(self.session, self.u_viewer, self.c1.id, "case:update")
        self.assertEqual(cm.exception.status_code, 404)
