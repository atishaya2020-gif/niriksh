import unittest

import jwt
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

from app.api.auth import seed_admin
from app.core.config import settings
from app.core.roles import VALID_ROLES, normalize_role
from app.core.security import create_access_token
from app.db.models import AccessRequest, Base, User
from app.schemas.auth import UserResponse
from app.services.authorization import (
    build_authorized_scope,
    has_case_capability,
    has_global_capability,
)


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)


def make_user(username="u", role="ADMIN"):
    return User(username=username, password_hash="hash", role=role)


class TestNormalizeRole(unittest.TestCase):
    def test_lowercase_admin_normalizes(self):
        self.assertEqual(normalize_role("admin"), "ADMIN")

    def test_mixed_case_super_admin_recognized(self):
        self.assertEqual(normalize_role("super_admin"), "SUPER_ADMIN")
        self.assertEqual(normalize_role(" Super_Admin "), "SUPER_ADMIN")

    def test_canonical_roles_preserved(self):
        self.assertEqual(normalize_role("ADMIN"), "ADMIN")
        self.assertEqual(normalize_role("SUPER_ADMIN"), "SUPER_ADMIN")

    def test_unknown_role_gets_no_capabilities(self):
        self.assertNotIn("BOGUS", VALID_ROLES)
        self.assertEqual(normalize_role("bogus"), "UNKNOWN")
        user = make_user(role="bogus")
        self.assertFalse(has_global_capability(user, "case:view"))
        self.assertFalse(has_global_capability(user, "admin:manage_users"))

    def test_lowercase_admin_has_admin_ceiling_at_boundary(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            user = make_user(role="admin")
            session.add(user)
            session.commit()
            scope = build_authorized_scope(session, user)
            self.assertEqual(scope.role, "ADMIN")
            self.assertIn("admin:manage_users", scope.global_capabilities)
            self.assertTrue(has_global_capability(user, "admin:manage_users"))
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_mixed_case_super_admin_is_super_admin_at_boundary(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            user = make_user(role="super_admin")
            session.add(user)
            session.commit()
            scope = build_authorized_scope(session, user)
            self.assertEqual(scope.role, "SUPER_ADMIN")
            self.assertTrue(scope.is_super_admin)
            self.assertTrue(has_global_capability(user, "admin:manage_users"))
            self.assertTrue(has_case_capability(session, user, 1, "case:view"))
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_unknown_role_has_no_case_capability(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            user = make_user(role="bogus")
            session.add(user)
            session.commit()
            scope = build_authorized_scope(session, user)
            self.assertEqual(scope.global_capabilities, set())
            self.assertFalse(has_case_capability(session, user, 1, "case:view"))
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_model_defaults_are_canonical_uppercase(self):
        self.assertEqual(User.__table__.c.role.default.arg, "INVESTIGATOR")
        self.assertEqual(
            AccessRequest.__table__.c.requested_role.default.arg, "INVESTIGATOR"
        )

    def test_seed_admin_uses_canonical_admin(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            seed_admin(session)
            seeded = (
                session.query(User)
                .filter(User.username == settings.admin_username)
                .first()
            )
            self.assertIsNotNone(seeded)
            self.assertEqual(seeded.role, "ADMIN")
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_seed_admin_normalizes_existing_lowercase(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            session.add(
                User(
                    username=settings.admin_username,
                    password_hash="hash",
                    role="admin",
                )
            )
            session.commit()
            seed_admin(session)
            seeded = (
                session.query(User)
                .filter(User.username == settings.admin_username)
                .first()
            )
            self.assertEqual(seeded.role, "ADMIN")
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_jwt_claim_uses_canonical_role(self):
        user = make_user(role="admin")
        user.id = 1
        token = create_access_token(user)
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        self.assertEqual(payload["role"], "ADMIN")

    def test_me_schema_exposes_canonical_role(self):
        user = make_user(role="admin")
        user.id = 1
        response = UserResponse.model_validate(user)
        self.assertEqual(response.role, "ADMIN")


if __name__ == "__main__":
    unittest.main()
