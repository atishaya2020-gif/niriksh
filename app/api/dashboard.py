from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User, Case, RawRecord, Alert
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def neo4j_count(query: str) -> int:
    rows = neo4j_client.execute(query)
    return int(rows[0]["count"]) if rows else 0


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # PostgreSQL metrics
    total_cases = db.query(Case).count()
    total_records = db.query(RawRecord).count()

    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.status.in_(
                ["NEW", "UNDER_REVIEW"]
            )
        )
        .count()
    )

    # Neo4j metrics
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