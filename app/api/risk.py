from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.models import User
from app.db.neo4j import neo4j_client
from app.services.risk import calculate_entity_risk

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])


@router.get("/entity/{entity_id}")
def entity_risk(
    entity_id: str,
    user: User = Depends(get_current_user),
):
    result = calculate_entity_risk(entity_id)

    if result.get("risk_score") == 0 and result.get("reasons") == ["Entity not found"]:
        raise HTTPException(status_code=404, detail="Entity not found")

    return {
        "success": True,
        "data": result,
        "message": "Investigative risk analysis generated",
    }


@router.get("/top")
def top_risk_entities(
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    limit = max(1, min(limit, 25))

    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[r]-()
    WITH p, count(DISTINCT r) AS connections
    ORDER BY connections DESC
    LIMIT $limit

    RETURN
        p.entity_id AS entity_id,
        p.name AS label,
        connections
    """

    rows = neo4j_client.execute(query, limit=limit)

    results = []

    for row in rows:
        risk = calculate_entity_risk(row["entity_id"])
        results.append(risk)

    results.sort(
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    return {
        "success": True,
        "data": {
            "entities": results,
            "count": len(results),
        },
        "message": "Top investigative risk indicators generated",
    }
