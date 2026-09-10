from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import (
    MATCH_STATUSES,
    Case,
    EntityMatch,
    User,
)
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.schemas.matches import EntityMatchResponse, MatchReview
from app.services.matching_service import generate_case_entity_matches

router = APIRouter(prefix="/matches", tags=["Entity Matching"])


@router.get("", response_model=dict)
def list_matches(
    case_id: int | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(EntityMatch)
    if case_id is not None:
        query = query.filter(EntityMatch.case_id == case_id)
    if status:
        query = query.filter(EntityMatch.status == status.upper())

    total = query.count()
    items = (
        query.order_by(EntityMatch.match_score.desc(), EntityMatch.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            EntityMatchResponse.model_validate(item).model_dump()
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{match_id}", response_model=EntityMatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    match = db.get(EntityMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Entity match not found")
    return match


@router.patch("/{match_id}/review")
def review_match(
    match_id: int,
    payload: MatchReview,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    match = db.get(EntityMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Entity match not found")

    status = payload.status.upper()
    if status not in MATCH_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(MATCH_STATUSES)}",
        )

    match.status = status
    match.reviewed_by = user.id
    match.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    # If confirmed, create a MATCHED_WITH relationship in Neo4j explicitly marked as human-reviewed
    if status == "CONFIRMED":
        try:
            cypher = """
            MATCH (s {entity_id: $source_id}), (c {entity_id: $candidate_id})
            MERGE (s)-[r:MATCHED_WITH {case_id: $case_id}]->(c)
            SET r.human_reviewed = true,
                r.reviewed_by = $user_id,
                r.reviewed_at = datetime()
            """
            neo4j_client.execute(
                cypher,
                source_id=match.source_entity_id,
                candidate_id=match.candidate_entity_id,
                case_id=match.case_id,
                user_id=user.id,
            )
        except Exception:
            pass
    elif status in ("REJECTED", "PENDING_REVIEW"):
        try:
            cypher = """
            MATCH (s {entity_id: $source_id})-[r:MATCHED_WITH {case_id: $case_id}]-(c {entity_id: $candidate_id})
            DELETE r
            """
            neo4j_client.execute(
                cypher,
                source_id=match.source_entity_id,
                candidate_id=match.candidate_entity_id,
                case_id=match.case_id,
            )
        except Exception:
            pass

    return {
        "success": True,
        "data": EntityMatchResponse.model_validate(match).model_dump(),
        "message": f"Entity match status updated to {status}",
    }


@router.post("/cases/{case_id}/generate")
def generate_matches_for_case(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    matches = generate_case_entity_matches(db, case_id)
    return {
        "success": True,
        "data": {
            "case_id": case_id,
            "generated_count": len(matches),
            "matches": [
                EntityMatchResponse.model_validate(m).model_dump()
                for m in matches
            ],
        },
        "message": "Potential entity matches generated",
    }
