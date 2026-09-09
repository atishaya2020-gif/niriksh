from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Case, RawRecord, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.services.risk import calculate_entity_risk

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


def extract_entity_label(entity_type: str, props: dict, default_label: str) -> str:
    if entity_type == "Person":
        return props.get("name") or default_label
    elif entity_type == "Phone":
        return props.get("value") or default_label
    elif entity_type == "BankAccount":
        return props.get("masked") or props.get("value") or default_label
    elif entity_type == "Device":
        return props.get("imei") or props.get("value") or default_label
    elif entity_type == "Location":
        return props.get("name") or default_label
    elif entity_type == "FIR":
        return props.get("fir_number") or props.get("value") or default_label
    elif entity_type == "SocialAccount":
        return props.get("handle") or props.get("value") or default_label
    elif entity_type == "Transaction":
        return props.get("transaction_id") or props.get("value") or default_label
    elif entity_type in ("Merchant", "PoliceStation"):
        return props.get("name") or default_label
    return default_label


@router.get("")
def search(
    q: str = Query(..., description="Search query string (minimum 2 characters)"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results to return"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Global investigative discovery search across the Niriksh data graph and case records.

    Searches entities across Neo4j (Person, Phone, BankAccount, Device, Location,
    FIR, SocialAccount, Transaction, Merchant, PoliceStation) and PostgreSQL cases.

    Investigative Note:
    Matches and network associations are analytical signals only. They do not
    establish identity, guilt, or criminal responsibility and require human verification.
    """
    search_query = q.strip()
    if len(search_query) < 2:
        raise HTTPException(
            status_code=422,
            detail="Query string must be at least 2 characters long after stripping whitespace",
        )

    results = []

    # 1. Search Neo4j Graph Entities
    neo4j_cypher = """
    MATCH (n)
    WHERE (
        n:Person OR n:Phone OR n:BankAccount OR n:Device OR n:Location OR
        n:FIR OR n:SocialAccount OR n:Transaction OR n:Merchant OR n:PoliceStation
    )
    AND (
        toLower(coalesce(n.name, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.value, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.entity_id, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.masked, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.bank_name, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.imei, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.fir_number, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.platform, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.handle, '')) CONTAINS toLower($search)
        OR toLower(coalesce(n.transaction_id, '')) CONTAINS toLower($search)
    )
    OPTIONAL MATCH (r:Record)--(n)
    WITH n,
         [l IN labels(n) WHERE l IN [
             'Person', 'Phone', 'BankAccount', 'Device', 'Location',
             'FIR', 'SocialAccount', 'Transaction', 'Merchant', 'PoliceStation'
         ]][0] AS entity_type,
         properties(n) AS properties,
         collect(DISTINCT r.case_id) AS raw_case_ids,
         count(DISTINCT r) AS record_count
    WITH n, entity_type, properties,
         [c IN raw_case_ids WHERE c IS NOT NULL] AS case_ids,
         record_count
    RETURN n.entity_id AS entity_id,
           entity_type,
           coalesce(n.name, n.handle, n.fir_number, n.transaction_id, n.masked, n.imei, n.value, n.entity_id) AS default_label,
           properties,
           case_ids,
           size(case_ids) AS case_count,
           record_count
    ORDER BY case_count DESC, record_count DESC, default_label
    LIMIT $limit
    """

    neo4j_rows = neo4j_client.execute(neo4j_cypher, search=search_query, limit=limit)

    for row in neo4j_rows:
        entity_id = row["entity_id"]
        entity_type = row["entity_type"] or "Entity"
        props = row.get("properties") or {}
        label = extract_entity_label(entity_type, props, row.get("default_label") or entity_id)

        case_ids = [int(c) for c in (row.get("case_ids") or [])]
        record_count = int(row.get("record_count") or 0)
        cross_case = len(case_ids) > 1

        risk_level = None
        risk_score = None

        if entity_type == "Person":
            try:
                risk_res = calculate_entity_risk(entity_id)
                risk_level = risk_res.get("risk_level", "LOW")
                risk_score = int(risk_res.get("risk_score", 0))
            except Exception:
                risk_level = "LOW"
                risk_score = 0

        results.append(
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "label": label,
                "risk": risk_level,
                "risk_score": risk_score,
                "case_ids": case_ids,
                "record_count": record_count,
                "cross_case": cross_case,
            }
        )

    # 2. Search PostgreSQL Cases
    case_query = (
        db.query(Case)
        .filter(
            (Case.case_number.ilike(f"%{search_query}%"))
            | (Case.title.ilike(f"%{search_query}%"))
            | (Case.description.ilike(f"%{search_query}%"))
        )
        .limit(limit)
        .all()
    )

    if case_query:
        found_case_ids = [c.id for c in case_query]
        counts_by_case = dict(
            db.query(RawRecord.case_id, func.count(RawRecord.id))
            .filter(RawRecord.case_id.in_(found_case_ids))
            .group_by(RawRecord.case_id)
            .all()
        )

        for c in case_query:
            rec_cnt = int(counts_by_case.get(c.id, 0))
            results.append(
                {
                    "entity_id": f"case:{c.id}",
                    "entity_type": "Case",
                    "label": c.case_number,
                    "risk": None,
                    "risk_score": None,
                    "case_ids": [c.id],
                    "record_count": rec_cnt,
                    "cross_case": False,
                }
            )

    # Limit total combined results
    final_results = results[:limit]

    return {
        "query": search_query,
        "results": final_results,
        "count": len(final_results),
    }
