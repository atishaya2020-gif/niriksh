from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import (
    EVIDENCE_TYPES,
    VERIFICATION_STATUSES,
    Case,
    Evidence,
    RawRecord,
    User,
)
from app.db.postgres import get_db
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceVerify,
)

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("/cases/{case_id}/evidence", response_model=EvidenceResponse)
def create_evidence(
    case_id: int,
    payload: EvidenceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_type = payload.evidence_type.upper()
    if evidence_type not in EVIDENCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid evidence_type. Allowed: {sorted(EVIDENCE_TYPES)}",
        )

    if payload.record_id is not None:
        record_exists = (
            db.query(RawRecord.id)
            .filter(
                RawRecord.case_id == case_id,
                RawRecord.record_id == payload.record_id,
            )
            .first()
        )
        if not record_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Record '{payload.record_id}' not found in case {case_id}",
            )

    evidence = Evidence(
        case_id=case_id,
        record_id=payload.record_id,
        evidence_type=evidence_type,
        source=payload.source,
        description=payload.description,
        collection_timestamp=payload.collection_timestamp,
        verification_status="PENDING",
        confidence=payload.confidence,
        evidence_metadata=payload.evidence_metadata,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


@router.get("/cases/{case_id}/evidence")
def list_case_evidence(
    case_id: int,
    evidence_type: str | None = None,
    verification_status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    query = db.query(Evidence).filter(Evidence.case_id == case_id)

    if evidence_type:
        query = query.filter(Evidence.evidence_type == evidence_type.upper())
    if verification_status:
        query = query.filter(
            Evidence.verification_status == verification_status.upper()
        )

    total = query.count()
    items = (
        query.order_by(Evidence.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            EvidenceResponse.model_validate(item).model_dump()
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.patch("/{evidence_id}/verify")
def verify_evidence(
    evidence_id: int,
    payload: EvidenceVerify,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    status = payload.status.upper()
    if status not in VERIFICATION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(VERIFICATION_STATUSES)}",
        )

    evidence.verification_status = status
    if payload.confidence is not None:
        evidence.confidence = payload.confidence
    evidence.verified_by = user.id
    evidence.verified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(evidence)

    return {
        "success": True,
        "data": {
            "id": evidence.id,
            "verification_status": evidence.verification_status,
            "confidence": evidence.confidence,
            "verified_by": evidence.verified_by,
            "verified_at": evidence.verified_at,
        },
        "message": "Evidence verification status updated",
    }
