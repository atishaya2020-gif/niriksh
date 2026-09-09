from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Alert, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.services.alert_service import generate_risk_alerts

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def list_alerts(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status.upper())

    alerts = (
        query
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "data": {
            "alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "entity_id": alert.entity_id,
                    "case_id": alert.case_id,
                    "risk_level": alert.risk_level,
                    "risk_score": alert.risk_score,
                    "reason": alert.reason,
                    "confidence": alert.confidence,
                    "status": alert.status,
                    "assigned_to": alert.assigned_to,
                    "created_at": alert.created_at,
                }
                for alert in alerts
            ],
            "count": len(alerts),
        },
        "message": "Alerts retrieved",
    }


@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "success": True,
        "data": {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "entity_id": alert.entity_id,
            "case_id": alert.case_id,
            "risk_level": alert.risk_level,
            "risk_score": alert.risk_score,
            "reason": alert.reason,
            "confidence": alert.confidence,
            "status": alert.status,
            "assigned_to": alert.assigned_to,
            "created_at": alert.created_at,
        },
        "message": "Alert retrieved",
    }


@router.post("/generate")
def generate_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[r]-()
    WITH p, count(DISTINCT r) AS connections
    WHERE connections >= 15
    RETURN p.entity_id AS entity_id
    ORDER BY connections DESC
    LIMIT 25
    """

    rows = neo4j_client.execute(query)

    entity_ids = [
        row["entity_id"]
        for row in rows
        if row.get("entity_id")
    ]

    alerts = generate_risk_alerts(db, entity_ids)

    return {
        "success": True,
        "data": {
            "generated": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "entity_id": alert.entity_id,
                    "risk_level": alert.risk_level,
                    "risk_score": alert.risk_score,
                    "reason": alert.reason,
                    "confidence": alert.confidence,
                    "status": alert.status,
                }
                for alert in alerts
            ],
        },
        "message": "Analytical alerts generated",
    }


@router.patch("/{alert_id}/status")
def update_alert_status(
    alert_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    allowed = {
        "NEW",
        "UNDER_REVIEW",
        "RESOLVED",
        "DISMISSED",
    }

    status = status.upper()

    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(allowed)}",
        )

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = status
    db.commit()
    db.refresh(alert)

    return {
        "success": True,
        "data": {
            "id": alert.id,
            "status": alert.status,
        },
        "message": "Alert status updated",
    }