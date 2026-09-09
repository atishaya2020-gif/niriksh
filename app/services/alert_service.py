from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Alert
from app.db.neo4j import neo4j_client
from app.services.risk import calculate_entity_risk


def find_entity_cases(
    entity_id: str,
) -> list[int]:
    query = """
    MATCH (r:Record)--(n {entity_id: $entity_id})
    RETURN DISTINCT r.case_id AS case_id
    ORDER BY case_id
    """

    rows = neo4j_client.execute(
        query,
        entity_id=entity_id,
    )

    return [
        int(row["case_id"])
        for row in rows
        if row.get("case_id") is not None
    ]


def create_alert_if_new(
    db: Session,
    *,
    alert_type: str,
    entity_id: str,
    case_id: int | None,
    risk_level: str,
    risk_score: int,
    reason: str,
    confidence: float,
) -> Alert | None:
    existing = (
        db.query(Alert)
        .filter(
            Alert.alert_type == alert_type,
            Alert.entity_id == entity_id,
            Alert.case_id == case_id,
            Alert.status.in_(["NEW", "UNDER_REVIEW"]),
        )
        .first()
    )

    if existing:
        return existing

    alert = Alert(
        alert_type=alert_type,
        entity_id=entity_id,
        case_id=case_id,
        risk_level=risk_level,
        risk_score=risk_score,
        reason=reason,
        confidence=confidence,
        status="NEW",
    )

    db.add(alert)
    db.flush()

    return alert


def generate_risk_alerts(
    db: Session,
    entity_ids: list[str],
) -> list[Alert]:
    created: list[Alert] = []

    for entity_id in entity_ids:
        result = calculate_entity_risk(entity_id)

        score = result.get("risk_score", 0)
        level = result.get("risk_level", "LOW")
        confidence = result.get("confidence", 0.0)
        reasons = result.get("reasons", [])

        if score < 40:
            continue

        if level == "HIGH":
            alert_type = "HIGH_RISK_ENTITY"
        else:
            alert_type = "NETWORK_CLUSTER"

        reason = "; ".join(reasons[:3])

        case_ids = find_entity_cases(entity_id)

        # If the entity exists in one or more cases,
        # create a case-specific alert for each case.
        if case_ids:
            for case_id in case_ids:
                alert = create_alert_if_new(
                    db,
                    alert_type=alert_type,
                    entity_id=entity_id,
                    case_id=case_id,
                    risk_level=level,
                    risk_score=score,
                    reason=reason,
                    confidence=confidence,
                )

                if alert:
                    created.append(alert)

        else:
            # Keep the alert even if no case can be resolved.
            alert = create_alert_if_new(
                db,
                alert_type=alert_type,
                entity_id=entity_id,
                case_id=None,
                risk_level=level,
                risk_score=score,
                reason=reason,
                confidence=confidence,
            )

            if alert:
                created.append(alert)

    db.commit()

    return created