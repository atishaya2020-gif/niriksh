from __future__ import annotations

from typing import Any

from app.db.neo4j import neo4j_client


def calculate_entity_risk(entity_id: str) -> dict[str, Any]:
    """
    Explainable investigative risk scoring.

    This is an analytical signal only.
    It does not determine guilt or criminality.
    """

    query = """
    MATCH (e {entity_id: $entity_id})

    OPTIONAL MATCH (e)-[r]-()
    WITH e, count(DISTINCT r) AS connections

    OPTIONAL MATCH (e)-[]-(phone:Phone)
    WITH e, connections, count(DISTINCT phone) AS phones

    OPTIONAL MATCH (e)-[]-(device:Device)
    WITH e, connections, phones, count(DISTINCT device) AS devices

    OPTIONAL MATCH (e)-[]-(account:BankAccount)
    WITH e, connections, phones, devices, count(DISTINCT account) AS accounts

    OPTIONAL MATCH (e)-[]-(record:Record)
    WITH e, connections, phones, devices, accounts,
         collect(DISTINCT record.case_id) AS case_ids,
         collect(DISTINCT record.fraud_flag) AS fraud_flags

    RETURN
        e.entity_id AS entity_id,
        labels(e)[0] AS entity_type,
        coalesce(e.name, e.value, e.entity_id) AS label,
        connections,
        phones,
        devices,
        accounts,
        size(case_ids) AS case_count,
        fraud_flags
    """

    rows = neo4j_client.execute(query, entity_id=entity_id)

    if not rows:
        return {
            "entity_id": entity_id,
            "risk_score": 0,
            "risk_level": "LOW",
            "reasons": ["Entity not found"],
            "confidence": 0.0,
            "requires_human_verification": True,
        }

    data = rows[0]

    connections = int(data.get("connections") or 0)
    phones = int(data.get("phones") or 0)
    devices = int(data.get("devices") or 0)
    accounts = int(data.get("accounts") or 0)
    case_count = int(data.get("case_count") or 0)

    fraud_flags = [
        str(value).strip().lower()
        for value in (data.get("fraud_flags") or [])
        if value is not None
    ]

    score = 0
    reasons: list[str] = []

    # Network connectivity
    if connections >= 40:
        score += 30
        reasons.append("Very high network connectivity")
    elif connections >= 25:
        score += 22
        reasons.append("High network connectivity")
    elif connections >= 15:
        score += 14
        reasons.append("Elevated network connectivity")
    elif connections >= 8:
        score += 7
        reasons.append("Multiple network connections")

    # Cross-case presence
    if case_count >= 3:
        score += 25
        reasons.append("Associated with records across multiple cases")
    elif case_count == 2:
        score += 15
        reasons.append("Associated with records across two cases")

    # Shared communication identifiers
    if phones >= 2:
        score += 12
        reasons.append("Associated with multiple phone identifiers")
    elif phones == 1:
        score += 4

    # Device reuse
    if devices >= 2:
        score += 12
        reasons.append("Associated with multiple devices")
    elif devices == 1:
        score += 3

    # Financial-account association
    if accounts >= 2:
        score += 12
        reasons.append("Associated with multiple financial accounts")
    elif accounts == 1:
        score += 4

    # Fraud-associated records
    fraud_positive = sum(
        1 for flag in fraud_flags
        if flag in {"yes", "true", "1"}
    )

    if fraud_positive >= 3:
        score += 20
        reasons.append("Multiple associated records contain fraud indicators")
    elif fraud_positive >= 1:
        score += 10
        reasons.append("An associated record contains a fraud indicator")

    score = min(score, 100)

    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Confidence reflects signal coverage, not probability of guilt.
    signal_count = sum(
        [
            connections > 0,
            phones > 0,
            devices > 0,
            accounts > 0,
            case_count > 0,
            fraud_positive > 0,
        ]
    )

    confidence = min(0.55 + (signal_count * 0.06), 0.90)

    if not reasons:
        reasons.append("Limited analytical signals available")

    return {
        "entity_id": data["entity_id"],
        "entity_type": data["entity_type"],
        "label": data["label"],
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "confidence": round(confidence, 2),
        "supporting_signals": {
            "connections": connections,
            "phones": phones,
            "devices": devices,
            "financial_accounts": accounts,
            "case_count": case_count,
            "fraud_indicator_records": fraud_positive,
        },
        "requires_human_verification": True,
        "analysis_type": "Simulated analytical output",
    }