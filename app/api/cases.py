from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Alert, Case, Evidence, RawRecord, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.schemas.case import CaseCreate, CaseResponse


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post("", response_model=CaseResponse)
def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = Case(
        **payload.model_dump(),
        created_by=user.id,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


@router.get("", response_model=list[CaseResponse])
def list_cases(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Case)
        .order_by(Case.id.desc())
        .all()
    )


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return case


@router.get("/{case_id}/overview")
def get_case_overview(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    # ---------------------------------------------------------
    # PostgreSQL metrics
    # ---------------------------------------------------------

    record_count = (
        db.query(RawRecord)
        .filter(RawRecord.case_id == case_id)
        .count()
    )

    alert_count = (
        db.query(Alert)
        .filter(
            Alert.case_id == case_id,
            Alert.status.in_(["NEW", "UNDER_REVIEW"]),
        )
        .count()
    )

    # ---------------------------------------------------------
    # Entity count for this case
    # ---------------------------------------------------------

    entity_query = """
    MATCH (r:Record {case_id: $case_id})--(n)
    WHERE NOT n:Record
    RETURN count(DISTINCT n) AS count
    """

    entity_rows = neo4j_client.execute(
        entity_query,
        case_id=case_id,
    )

    entity_count = (
        int(entity_rows[0]["count"])
        if entity_rows
        else 0
    )

    # ---------------------------------------------------------
    # Relationship count for this case
    # ---------------------------------------------------------

    relationship_query = """
    MATCH (r:Record {case_id: $case_id})-[rel]-()
    RETURN count(DISTINCT rel) AS count
    """

    relationship_rows = neo4j_client.execute(
        relationship_query,
        case_id=case_id,
    )

    relationship_count = (
        int(relationship_rows[0]["count"])
        if relationship_rows
        else 0
    )

    # ---------------------------------------------------------
    # Key investigative entities
    #
    # Prioritize people instead of locations/other entities.
    # The complete network is still available through /graph.
    # ---------------------------------------------------------

    key_entities_query = """
    MATCH (r:Record {case_id: $case_id})--(n:Person)
    WITH n, count(*) AS connections
    ORDER BY connections DESC
    LIMIT 10

    RETURN
        n.entity_id AS entity_id,
        labels(n)[0] AS entity_type,
        coalesce(n.name, n.value, n.entity_id) AS label,
        connections
    """

    key_entity_rows = neo4j_client.execute(
        key_entities_query,
        case_id=case_id,
    )

    key_entities = [
        {
            "entity_id": row["entity_id"],
            "entity_type": row["entity_type"],
            "label": row["label"],
            "connections": int(row["connections"]),
        }
        for row in key_entity_rows
    ]

    # ---------------------------------------------------------
    # Recent alerts for this case
    # ---------------------------------------------------------

    alerts = (
        db.query(Alert)
        .filter(Alert.case_id == case_id)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )

    alert_data = [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "entity_id": alert.entity_id,
            "risk_level": alert.risk_level,
            "risk_score": alert.risk_score,
            "reason": alert.reason,
            "confidence": alert.confidence,
            "status": alert.status,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return {
        "success": True,
        "data": {
            "case": {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "description": case.description,
                "created_at": case.created_at,
            },
            "investigation": {
                "status": "ACTIVE",
                "risk_level": (
                    "HIGH"
                    if alert_count > 0
                    else "MEDIUM"
                ),
                "requires_human_verification": True,
            },
            "metrics": {
                "records": record_count,
                "entities": entity_count,
                "relationships": relationship_count,
                "active_alerts": alert_count,
            },
            "key_entities": key_entities,
            "alerts": alert_data,
            "analysis_note": (
                "Network connectivity and risk indicators "
                "are investigative signals and require "
                "human verification."
            ),
        },
        "message": "Case investigation overview retrieved",
    }


@router.get("/{case_id}/timeline")
def get_case_timeline(
    case_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    events = []

    events.append({
        "timestamp": case.created_at,
        "event_type": "CASE_CREATED",
        "description": f"Case '{case.title}' created",
        "case_id": case.id,
        "record_id": None,
        "entity_id": None,
        "source": "case",
    })

    raw_records = (
        db.query(RawRecord)
        .filter(RawRecord.case_id == case_id)
        .filter(RawRecord.incident_datetime.isnot(None))
        .all()
    )

    for rec in raw_records:
        events.append({
            "timestamp": rec.incident_datetime,
            "event_type": f"RECORD_{rec.category.upper().replace(' ', '_')}",
            "description": f"Incident recorded in {rec.category} (record {rec.record_id})",
            "case_id": case_id,
            "record_id": rec.record_id,
            "entity_id": None,
            "source": rec.category.lower(),
        })

    alerts = (
        db.query(Alert)
        .filter(Alert.case_id == case_id)
        .all()
    )

    for alert in alerts:
        events.append({
            "timestamp": alert.created_at,
            "event_type": "ALERT_GENERATED",
            "description": f"Alert: {alert.alert_type} ({alert.risk_level} risk)",
            "case_id": case_id,
            "record_id": None,
            "entity_id": alert.entity_id,
            "source": "alert_service",
        })

    evidences = (
        db.query(Evidence)
        .filter(Evidence.case_id == case_id)
        .all()
    )

    for ev in evidences:
        events.append({
            "timestamp": ev.created_at,
            "event_type": "EVIDENCE_COLLECTED",
            "description": f"Evidence collected: {ev.evidence_type} from {ev.source}",
            "case_id": case_id,
            "record_id": ev.record_id,
            "entity_id": None,
            "source": "evidence",
        })

        if ev.verified_at is not None:
            events.append({
                "timestamp": ev.verified_at,
                "event_type": f"EVIDENCE_{ev.verification_status}",
                "description": f"Evidence #{ev.id} {ev.verification_status.lower().replace('_', ' ')}",
                "case_id": case_id,
                "record_id": ev.record_id,
                "entity_id": None,
                "source": "evidence_review",
            })

    events.sort(
        key=lambda e: e["timestamp"] if e["timestamp"] else "",
    )

    total = len(events)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": events[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
    }