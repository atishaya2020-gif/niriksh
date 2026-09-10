from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Case, User
from app.db.neo4j import neo4j_client
from app.db.postgres import get_db
from app.services.risk import calculate_entity_risk


router = APIRouter(
    prefix="/network",
    tags=["Network"],
)


@router.get("/{case_id}")
def get_case_network(
    case_id: int,
    limit: int = Query(
        40,
        ge=10,
        le=100,
    ),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Verify case exists
    # --------------------------------------------------------

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    # --------------------------------------------------------
    # Find the most connected people in this case.
    #
    # We use a bounded number of primary people so the
    # frontend receives a manageable Cytoscape graph.
    # --------------------------------------------------------

    people_query = """
    MATCH (r:Record {case_id: $case_id})--(p:Person)
    WITH
        p,
        count(DISTINCT r) AS record_connections
    ORDER BY record_connections DESC
    LIMIT $limit

    RETURN
        p.entity_id AS person_id,
        p.name AS person_name,
        record_connections
    """

    people_rows = neo4j_client.execute(
        people_query,
        case_id=case_id,
        limit=limit,
    )

    if not people_rows:
        return {
            "success": True,
            "data": {
                "case": {
                    "id": case.id,
                    "case_number": case.case_number,
                    "title": case.title,
                },
                "network": {
                    "nodes": [],
                    "edges": [],
                },
                "summary": {
                    "nodes": 0,
                    "edges": 0,
                    "primary_entities": 0,
                },
                "analysis_note": (
                    "No network entities were found "
                    "for this case."
                ),
            },
            "message": (
                "Investigation network retrieved"
            ),
        }

    # --------------------------------------------------------
    # Extract primary person IDs
    # --------------------------------------------------------

    person_ids = [
        row["person_id"]
        for row in people_rows
        if row.get("person_id")
    ]

    # --------------------------------------------------------
    # Get the bounded network around those people.
    #
    # Returning relationship type as a string avoids relying
    # on Neo4j driver relationship objects in Python.
    # --------------------------------------------------------

    network_query = """
    MATCH (p:Person)-[r]-(other)
    WHERE p.entity_id IN $person_ids
      AND type(r) <> 'MATCHED_WITH'

    RETURN
        p.entity_id AS source_id,
        p.name AS source_name,

        other.entity_id AS target_id,
        labels(other)[0] AS target_type,
        coalesce(
            other.name,
            other.value,
            other.entity_id
        ) AS target_label,

        type(r) AS relationship_type
    """

    network_rows = neo4j_client.execute(
        network_query,
        person_ids=person_ids,
    )

    # --------------------------------------------------------
    # Build unique nodes
    # --------------------------------------------------------

    nodes = {}

    for row in people_rows:
        person_id = row.get("person_id")

        if not person_id:
            continue

        person_name = (
            row.get("person_name")
            or person_id
        )

        connections = int(
            row.get("record_connections") or 0
        )

        # Use the actual risk engine for primary people.
        try:
            risk_result = calculate_entity_risk(
                person_id
            )

            risk_level = risk_result.get(
                "risk_level",
                "LOW",
            )

            risk_score = int(
                risk_result.get(
                    "risk_score",
                    0,
                )
            )

        except Exception:
            # The graph should still load even if an
            # individual risk calculation fails.
            risk_level = "LOW"
            risk_score = 0

        nodes[person_id] = {
            "id": person_id,
            "label": person_name,
            "type": "Person",
            "risk": risk_level,
            "risk_score": risk_score,
            "metadata": {
                "record_connections": connections,
            },
        }

    # --------------------------------------------------------
    # Build connected nodes and edges
    # --------------------------------------------------------

    edges = {}

    for row in network_rows:
        source_id = row.get("source_id")
        target_id = row.get("target_id")
        relationship_type = row.get(
            "relationship_type"
        )

        if not source_id or not target_id:
            continue

        if not relationship_type:
            relationship_type = "CONNECTED_TO"

        # Add target node
        target_type = (
            row.get("target_type")
            or "Entity"
        )

        target_label = (
            row.get("target_label")
            or target_id
        )

        if target_id not in nodes:
            nodes[target_id] = {
                "id": target_id,
                "label": target_label,
                "type": target_type,
                "risk": "LOW",
                "risk_score": 0,
                "metadata": {},
            }

        # Prevent duplicate undirected relationships
        edge_key = tuple(
            sorted(
                [
                    source_id,
                    target_id,
                ]
            )
        ) + (relationship_type,)

        edge_id = "::".join(
            [
                edge_key[0],
                edge_key[2],
                edge_key[1],
            ]
        )

        if edge_id in edges:
            continue

        edges[edge_id] = {
            "id": edge_id,
            "source": source_id,
            "target": target_id,
            "relationship_type": relationship_type,
            "confidence": 0.8,
            "reason": (
                "Detected connection in "
                "the case network."
            ),
        }

    # --------------------------------------------------------
    # Keep graph bounded.
    #
    # A person can have many connections in the full
    # 10K-record graph. We cap the number of edges so
    # Cytoscape remains responsive.
    # --------------------------------------------------------

    max_edges = max(
        100,
        limit * 5,
    )

    bounded_edges = list(
        edges.values()
    )[:max_edges]

    # Keep only nodes actually participating in the
    # returned graph.
    used_node_ids = set()

    for edge in bounded_edges:
        used_node_ids.add(
            edge["source"]
        )
        used_node_ids.add(
            edge["target"]
        )

    bounded_nodes = [
        node
        for node in nodes.values()
        if node["id"] in used_node_ids
    ]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "success": True,
        "data": {
            "case": {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
            },

            "network": {
                "nodes": bounded_nodes,
                "edges": bounded_edges,
            },

            "summary": {
                "nodes": len(
                    bounded_nodes
                ),
                "edges": len(
                    bounded_edges
                ),
                "primary_entities": len(
                    person_ids
                ),
            },

            "analysis_note": (
                "Network connections are investigative "
                "signals. They do not establish identity, "
                "guilt, or criminal responsibility and "
                "require human verification."
            ),
        },

        "message": (
            "Investigation network retrieved"
        ),
    }