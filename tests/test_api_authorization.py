from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.pool import StaticPool
import unittest

from app.main import app
from app.db.models import Base, User, Case, CaseGrant, Jurisdiction, UserJurisdiction, CaseJurisdiction, RawRecord, ProcessingJob
from app.db.postgres import get_db

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)

class TestAPIAuthorization(unittest.TestCase):
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

        self.u_admin = User(username="admin", password_hash="h", role="ADMIN")
        self.u_investigator = User(username="inv1", password_hash="h", role="INVESTIGATOR")
        self.session.add_all([self.u_admin, self.u_investigator])
        self.session.commit()

        from app.core.security import create_access_token
        self.token = create_access_token(self.u_investigator)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_cases_get_authorized_success(self):
        c = Case(case_number="c1", title="c1")
        self.session.add(c)
        self.session.commit()
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=c.id, capability="case:view", granted_by=self.u_admin.id))
        self.session.commit()

        response = self.client.get(f"/api/cases/{c.id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_cases_get_unauthorized_404(self):
        c = Case(case_number="c2", title="c2")
        self.session.add(c)
        self.session.commit()
        response = self.client.get(f"/api/cases/{c.id}", headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_records_list_filtering(self):
        c1 = Case(case_number="c1", title="c1")
        c2 = Case(case_number="c2", title="c2")
        self.session.add_all([c1, c2])
        self.session.commit()

        # Grant access to c1 only
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=c1.id, capability="case:view", granted_by=self.u_admin.id))
        self.session.commit()

        self.session.add(RawRecord(record_id="r1", case_id=c1.id, category="test", payload={}))
        self.session.add(RawRecord(record_id="r2", case_id=c2.id, category="test", payload={}))
        self.session.commit()

        response = self.client.get("/api/records", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["case_id"], c1.id)

    def test_record_direct_lookup_authorization(self):
        c1 = Case(case_number="c1", title="c1")
        c2 = Case(case_number="c2", title="c2")
        self.session.add_all([c1, c2])
        self.session.commit()

        r1 = RawRecord(record_id="rec1", case_id=c1.id, category="test", payload={})
        r2 = RawRecord(record_id="rec2", case_id=c2.id, category="test", payload={})
        self.session.add_all([r1, r2])
        self.session.commit()

        # Grant view on c1
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=c1.id, capability="case:view", granted_by=self.u_admin.id))
        self.session.commit()

        # Look up rec1 -> Success
        res1 = self.client.get("/api/records/rec1", headers=self.headers)
        self.assertEqual(res1.status_code, 200)

        # Look up rec2 -> 404 (because owning case c2 is not authorized/viewable)
        res2 = self.client.get("/api/records/rec2", headers=self.headers)
        self.assertEqual(res2.status_code, 404)

    def test_upload_csv_authorization(self):
        c1 = Case(case_number="c1", title="c1")
        self.session.add(c1)
        self.session.commit()

        # Attempt upload without case:ingest -> 403
        files = {"file": ("test.csv", "col1,col2\nval1,val2", "text/csv")}
        res1 = self.client.post(f"/api/cases/{c1.id}/upload-csv", files=files, headers=self.headers)
        self.assertEqual(res1.status_code, 404)

        # Grant case:view but not case:ingest -> 403
        self.session.add(CaseGrant(user_id=self.u_investigator.id, case_id=c1.id, capability="case:view", granted_by=self.u_admin.id))
        self.session.commit()
        res2 = self.client.post(f"/api/cases/{c1.id}/upload-csv", files=files, headers=self.headers)
        self.assertEqual(res2.status_code, 403)
