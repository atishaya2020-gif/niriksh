from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import RawRecord, User
from app.db.postgres import get_db

router = APIRouter(prefix="/records", tags=["Records"])


def serialize_record(record: RawRecord):
    return {
        "id": record.id,
        "record_id": record.record_id,
        "case_id": record.case_id,
        "category": record.category,
        "incident_datetime": record.incident_datetime,
        "payload": record.payload,
        "created_at": record.created_at,
    }


@router.get("")
def list_records(
    case_id: int | None = None,
    category: str | None = None,
    record_status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(RawRecord)
    if case_id is not None:
        query = query.filter(RawRecord.case_id == case_id)
    if category:
        query = query.filter(RawRecord.category == category)
    if record_status:
        query = query.filter(RawRecord.payload["record_status"].astext == record_status)
    total = query.count()
    records = query.order_by(RawRecord.incident_datetime.desc(), RawRecord.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [serialize_record(record) for record in records], "total": total, "page": page, "page_size": page_size}


@router.get("/{record_id}")
def get_record(record_id: str, case_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(RawRecord).filter(RawRecord.record_id == record_id)
    if case_id is not None:
        query = query.filter(RawRecord.case_id == case_id)
    record = query.first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return serialize_record(record)
