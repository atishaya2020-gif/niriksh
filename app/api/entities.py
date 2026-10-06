from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Alert, Case, RawRecord, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.services.risk import calculate_entity_risk


router = APIRouter(
    prefix="/entities",
    tags=["Entities"],
)


# ============================================================
# Entity Search
# ============================================================

from app.core.roles import normalize_role
from app.services.authorization import get_authorized_case_ids
from app.db.neo4j import get_provenance_filter

@router.get("")
def list_entities(
    entity_type: str | None = None,
    search: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    authorized_case_ids = list(get_authorized_case_ids(db, user, "network:view"))
    is_super_admin = (normalize_role(user.role) == "SUPER_ADMIN")

    if not authorized_case_ids and not is_super_admin:
        return []

    provenance_filter = get_provenance_filter()
    query = f"""
    MATCH (n)
    WHERE ($entity_type IS NULL OR $entity_type IN labels(n))
      AND ($search IS NULL OR toLower(coalesce(n.name, n.value, n.entity_id)) CONTAINS toLower($search))
      AND ($is_super_admin = true OR EXISTS {{
          MATCH (n)-[r]-(rel_target)
          WHERE {provenance_filter}
      }})

    RETURN
        n.entity_id AS id,
        labels(n)[0] AS type,
        coalesce(n.name, n.value, n.entity_id) AS label,
        properties(n) AS properties

    ORDER BY type, label
    LIMIT $limit
    """

    return neo4j_client.execute(
        query,
        entity_type=entity_type,
        search=search,
        limit=limit,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin
    )


# ============================================================
# Entity Investigation Profile
# ============================================================

@router.get("/{entity_id}")
def get_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Basic entity information
    # --------------------------------------------------------

    authorized_case_ids = list(get_authorized_case_ids(db, user, "network:view"))
    is_super_admin = (normalize_role(user.role) == "SUPER_ADMIN")
    provenance_filter = get_provenance_filter()

    query = f"""
    MATCH (n {{entity_id: $entity_id}})
    WHERE ($is_super_admin = true OR EXISTS {{
        MATCH (n)-[r]-(rel_target)
        WHERE {provenance_filter}
    }})
    RETURN
        n.entity_id AS id,
        labels(n)[0] AS type,
        coalesce(n.name, n.value, n.entity_id) AS label,
        properties(n) AS properties
    """

    rows = neo4j_client.execute(
        query,
        entity_id=entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Entity not found",
        )

    entity = rows[0]

    # --------------------------------------------------------
    # Explainable risk analysis
    # --------------------------------------------------------

    risk = calculate_entity_risk(
        entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin,
    )

    # --------------------------------------------------------
    # Connection summary
    # --------------------------------------------------------

    connection_summary_query = f"""
    MATCH (n {{entity_id: $entity_id}})-[r]-(other)
    WHERE type(r) <> 'MATCHED_WITH'
      AND ($is_super_admin = true OR {provenance_filter})

    RETURN
        type(r) AS relationship_type,
        labels(other)[0] AS connected_entity_type,
        count(*) AS count

    ORDER BY count DESC
    """

    connection_rows = neo4j_client.execute(
        connection_summary_query,
        entity_id=entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin,
    )

    connection_summary = [
        {
            "relationship_type": row["relationship_type"],
            "entity_type": row["connected_entity_type"],
            "count": int(row["count"]),
        }
        for row in connection_rows
    ]

    # --------------------------------------------------------
    # Case associations
    # --------------------------------------------------------

    case_query = f"""
    MATCH (r:Record)-[rel]-(n {{entity_id: $entity_id}})
    WHERE $is_super_admin = true OR (rel.case_id IN $authorized_case_ids OR ANY(c IN rel.evidence_case_ids WHERE c IN $authorized_case_ids))

    RETURN DISTINCT r.case_id AS case_id

    ORDER BY case_id
    """

    case_rows = neo4j_client.execute(
        case_query,
        entity_id=entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin,
    )

    case_ids = [
        int(row["case_id"])
        for row in case_rows
        if row.get("case_id") is not None
    ]

    cases = []

    if case_ids:
        case_records = (
            db.query(Case)
            .filter(Case.id.in_(case_ids))
            .order_by(Case.id.desc())
            .all()
        )

        cases = [
            {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "description": case.description,
                "created_at": case.created_at,
            }
            for case in case_records
        ]

    # --------------------------------------------------------
    # Entity timeline
    # --------------------------------------------------------

    timeline_query = f"""
    MATCH (r:Record)-[rel]-(n {{entity_id: $entity_id}})
    WHERE $is_super_admin = true OR (rel.case_id IN $authorized_case_ids OR ANY(c IN rel.evidence_case_ids WHERE c IN $authorized_case_ids))

    RETURN DISTINCT
        r.record_id AS record_id,
        r.case_id AS case_id,
        r.category AS category

    ORDER BY r.case_id DESC
    LIMIT 50
    """

    timeline_rows = neo4j_client.execute(
        timeline_query,
        entity_id=entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin,
    )

    record_pairs = {
        (
            row["case_id"],
            row["record_id"],
        )
        for row in timeline_rows
    }

    timeline = []

    if record_pairs:
        record_ids = [
            record_id
            for _, record_id in record_pairs
        ]

        records_query = db.query(RawRecord).filter(RawRecord.record_id.in_(record_ids))
        if not is_super_admin:
            records_query = records_query.filter(RawRecord.case_id.in_(authorized_case_ids))
        records = records_query.all()

        for record in records:
            if (
                record.case_id,
                record.record_id,
            ) not in record_pairs:
                continue

            timeline.append(
                {
                    "record_id": record.record_id,
                    "case_id": record.case_id,
                    "category": record.category,
                    "incident_datetime": record.incident_datetime,
                    "record_status": (
                        record.payload.get(
                            "record_status"
                        )
                    ),
                }
            )

    timeline.sort(
        key=lambda item: (
            item["incident_datetime"] or ""
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Related alerts
    # --------------------------------------------------------

    alerts_query = db.query(Alert).filter(Alert.entity_id == entity_id)
    if not is_super_admin:
        alerts_query = alerts_query.filter(Alert.case_id.in_(authorized_case_ids))
    alerts = alerts_query.order_by(Alert.created_at.desc()).limit(20).all()

    alert_data = [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "case_id": alert.case_id,
            "risk_level": alert.risk_level,
            "risk_score": alert.risk_score,
            "reason": alert.reason,
            "confidence": alert.confidence,
            "status": alert.status,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]

    # --------------------------------------------------------
    # Investigation profile
    # --------------------------------------------------------

    return {
        "success": True,
        "data": {
            "entity": {
                "id": entity["id"],
                "type": entity["type"],
                "label": entity["label"],
                "properties": entity["properties"],
            },

            "risk": {
                "score": risk.get(
                    "risk_score",
                    0,
                ),
                "level": risk.get(
                    "risk_level",
                    "LOW",
                ),
                "reasons": risk.get(
                    "reasons",
                    [],
                ),
                "confidence": risk.get(
                    "confidence",
                    0.0,
                ),
                "supporting_signals": risk.get(
                    "supporting_signals",
                    {},
                ),
                "requires_human_verification": True,
                "analysis_type": (
                    "Simulated analytical output"
                ),
            },

            "cases": {
                "count": len(cases),
                "items": cases,
            },

            "connections": {
                "total": sum(
                    item["count"]
                    for item in connection_summary
                ),
                "summary": connection_summary,
            },

            "timeline": {
                "count": len(timeline),
                "items": timeline,
            },

            "alerts": {
                "count": len(alert_data),
                "items": alert_data,
            },

            "investigative_note": (
                "Entity associations, risk indicators, "
                "and network patterns are analytical "
                "signals only. They do not establish "
                "identity, guilt, or criminal responsibility "
                "and require human verification."
            ),
        },

        "message": (
            "Entity investigation profile retrieved"
        ),
    }


# ============================================================
# Entity Connections
# ============================================================

@router.get("/{entity_id}/connections")
def entity_connections(
    entity_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    authorized_case_ids = list(get_authorized_case_ids(db, user, "network:view"))
    is_super_admin = (normalize_role(user.role) == "SUPER_ADMIN")
    if not authorized_case_ids and not is_super_admin:
        return []
    provenance_filter = get_provenance_filter()

    query = f"""
    MATCH (n {{entity_id: $entity_id}})-[r]-(other)
    WHERE type(r) <> 'MATCHED_WITH'
      AND ($is_super_admin = true OR (r.case_id IN $authorized_case_ids OR ANY(c IN r.evidence_case_ids WHERE c IN $authorized_case_ids)))
    RETURN
        other.entity_id AS id,
        labels(other)[0] AS type,
        coalesce(other.name, other.value, other.entity_id) AS label,
        properties(other) AS properties,
        type(r) AS relationship_type,
        properties(r) AS relationship_properties
    ORDER BY relationship_type, label
    LIMIT $limit
    """

    return neo4j_client.execute(
        query,
        entity_id=entity_id,
        limit=limit,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin
    )


# ============================================================
# Entity Timeline
# ============================================================

@router.get("/{entity_id}/timeline")
def entity_timeline(
    entity_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    authorized_case_ids = list(get_authorized_case_ids(db, user, "network:view"))
    is_super_admin = (normalize_role(user.role) == "SUPER_ADMIN")
    if not authorized_case_ids and not is_super_admin:
        return []
    provenance_filter = get_provenance_filter()

    query = f"""
    MATCH (r:Record)-[rel:MENTIONS]-(n {{entity_id: $entity_id}})
    WHERE ($is_super_admin = true OR (rel.case_id IN $authorized_case_ids OR ANY(c IN rel.evidence_case_ids WHERE c IN $authorized_case_ids)))
    RETURN DISTINCT
        r.record_id AS record_id,
        r.case_id AS case_id
    ORDER BY r.case_id DESC
    LIMIT 50
    """

    rows = neo4j_client.execute(
        query,
        entity_id=entity_id,
        authorized_case_ids=authorized_case_ids,
        is_super_admin=is_super_admin
    )

    if not rows:
        return []

    pairs = {
        (
            row["case_id"],
            row["record_id"],
        )
        for row in rows
    }

    record_ids = [
        record_id
        for _, record_id in pairs
    ]

    records = (
        db.query(RawRecord)
        .filter(
            RawRecord.record_id.in_(record_ids)
        )
        .all()
    )

    timeline = [
        {
            "record_id": record.record_id,
            "case_id": record.case_id,
            "category": record.category,
            "incident_datetime": (
                record.incident_datetime
            ),
            "record_status": (
                record.payload.get(
                    "record_status"
                )
            ),
        }
        for record in records
        if (
            record.case_id,
            record.record_id,
        ) in pairs
    ]

    return sorted(
        timeline,
        key=lambda item: (
            item["incident_datetime"] or ""
        ),
        reverse=True,
    )
