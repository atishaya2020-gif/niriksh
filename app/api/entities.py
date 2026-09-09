from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import RawRecord, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.get("")
def list_entities(
    entity_type: str | None = None,
    search: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
):
    query = """
    MATCH (n)
    WHERE ($entity_type IS NULL OR $entity_type IN labels(n))
      AND ($search IS NULL OR toLower(coalesce(n.name, n.value, n.entity_id)) CONTAINS toLower($search))
    RETURN n.entity_id AS id, labels(n)[0] AS type, coalesce(n.name, n.value, n.entity_id) AS label, properties(n) AS properties
    ORDER BY type, label
    LIMIT $limit
    """
    return neo4j_client.execute(query, entity_type=entity_type, search=search, limit=limit)


@router.get("/{entity_id}")
def get_entity(entity_id: str, user: User = Depends(get_current_user)):
    rows = neo4j_client.execute(
        "MATCH (n {entity_id:$entity_id}) RETURN n.entity_id AS id, labels(n)[0] AS type, coalesce(n.name,n.value,n.entity_id) AS label, properties(n) AS properties",
        entity_id=entity_id,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Entity not found")
    return rows[0]


@router.get("/{entity_id}/connections")
def entity_connections(entity_id: str, limit: int = Query(100, ge=1, le=500), user: User = Depends(get_current_user)):
    query = """
    MATCH (n {entity_id:$entity_id})-[r]-(other)
    RETURN other.entity_id AS id, labels(other)[0] AS type, coalesce(other.name,other.value,other.entity_id) AS label,
           properties(other) AS properties, type(r) AS relationship_type, properties(r) AS relationship_properties
    LIMIT $limit
    """
    return neo4j_client.execute(query, entity_id=entity_id, limit=limit)


@router.get("/{entity_id}/timeline")
def entity_timeline(entity_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = neo4j_client.execute(
        "MATCH (r:Record)-[]-(n {entity_id:$entity_id}) RETURN DISTINCT r.record_id AS record_id, r.case_id AS case_id",
        entity_id=entity_id,
    )
    if not rows:
        return []
    pairs = {(row["case_id"], row["record_id"]) for row in rows}
    records = db.query(RawRecord).filter(RawRecord.record_id.in_([record_id for _, record_id in pairs])).all()
    timeline = [
        {
            "record_id": record.record_id,
            "case_id": record.case_id,
            "category": record.category,
            "incident_datetime": record.incident_datetime,
            "record_status": record.payload.get("record_status"),
        }
        for record in records
        if (record.case_id, record.record_id) in pairs
    ]
    return sorted(timeline, key=lambda item: item["incident_datetime"] or "", reverse=True)
