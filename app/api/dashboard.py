from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.roles import normalize_role
from app.core.security import get_current_user
from app.db.models import User, Case, RawRecord, Alert
from app.db.neo4j import neo4j_client, get_provenance_filter
from app.db.postgres import get_db
from app.services.authorization import get_authorized_case_ids


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def neo4j_count(query: str, **params) -> int:
    rows = neo4j_client.execute(query, **params)
    return int(rows[0]["count"]) if rows else 0


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    role = normalize_role(user.role)
    is_super_admin = role == "SUPER_ADMIN"
    authorized_case_ids = list(get_authorized_case_ids(db, user, "case:view"))

    # PostgreSQL metrics
    if is_super_admin:
        total_cases = db.query(Case).count()
        total_records = db.query(RawRecord).count()
        active_alerts = db.query(Alert).filter(Alert.status.in_(["NEW", "UNDER_REVIEW"])).count()
    else:
        if not authorized_case_ids:
            total_cases = 0
            total_records = 0
            active_alerts = 0
        else:
            total_cases = db.query(Case).filter(Case.id.in_(authorized_case_ids)).count()
            total_records = db.query(RawRecord).filter(RawRecord.case_id.in_(authorized_case_ids)).count()
            # Alert scoping not safely established for this patch, fail closed
            active_alerts = 0

    # Neo4j metrics
    if is_super_admin:
        total_entities = neo4j_count(
            "MATCH (n) RETURN count(n) AS count"
        )
        detected_relationships = neo4j_count(
            "MATCH ()-[r]->() RETURN count(r) AS count"
        )
        high_risk_entities = neo4j_count(
            "MATCH (n) "
            "WHERE COUNT { (n)--() } >= 8 "
            "RETURN count(n) AS count"
        )
    else:
        if not authorized_case_ids:
            total_entities = 0
            detected_relationships = 0
            high_risk_entities = 0
        else:
            provenance = get_provenance_filter()
            total_entities = neo4j_count(
                f"MATCH (n)-[r]-(m) WHERE {provenance} RETURN count(DISTINCT n) AS count",
                authorized_case_ids=authorized_case_ids
            )
            detected_relationships = neo4j_count(
                f"MATCH (n)-[r]->(m) WHERE {provenance} RETURN count(r) AS count",
                authorized_case_ids=authorized_case_ids
            )
            high_risk_entities = neo4j_count(
                "MATCH (n)-[r]-(m) "
                f"WHERE {get_provenance_filter()} "
                "WITH n, count(DISTINCT r) AS degree "
                "WHERE degree >= 8 "
                "RETURN count(n) AS count",
                authorized_case_ids=authorized_case_ids
            )

    return {
        "success": True,
        "data": {
            "metrics": {
                "active_cases": total_cases,
                "total_cases": total_cases,
                "total_records": total_records,
                "total_entities": total_entities,
                "detected_relationships": detected_relationships,
                "high_risk_entities": high_risk_entities,
                "active_alerts": active_alerts,
            },
            "status": "operational",
            "risk_note": (
                "Connectivity is an investigative signal "
                "and requires human verification."
            ),
        },
        "message": "Dashboard metrics retrieved",
    }


@router.get("/metrics")
def dashboard_metrics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return dashboard(
        db=db,
        user=user,
    )