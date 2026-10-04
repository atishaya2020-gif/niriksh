
import pytest
from unittest.mock import MagicMock, patch
from app.services.matching_service import generate_case_entity_matches
from app.services.graph_service import get_graph
from sqlalchemy.orm import Session
from app.db.models import User

# A. User authorized for Case A requests Case A graph -> allowed.
@patch("app.services.graph_service.neo4j_client.execute")
@patch("app.services.graph_service.get_authorized_case_ids")
def test_graph_case_a_authorized(mock_get_auth_cases, mock_execute):
    mock_get_auth_cases.return_value = {1}
    user = MagicMock(spec=User)
    user.role = "INVESTIGATOR"
    get_graph(case_id=1, db=MagicMock(), user=user)

    # Should call Neo4j
    assert mock_execute.called
    assert mock_execute.call_args[1]["authorized_case_ids"] == [1]

# B. User authorized only for Case A requests Case B graph -> denied.
@patch("app.services.graph_service.neo4j_client.execute")
@patch("app.services.graph_service.get_authorized_case_ids")
def test_graph_case_b_unauthorized(mock_get_auth_cases, mock_execute):
    mock_get_auth_cases.return_value = {1}
    user = MagicMock(spec=User)
    user.role = "INVESTIGATOR"

    result = get_graph(case_id=2, db=MagicMock(), user=user)

    # Should terminate early
    assert result == {"nodes": [], "edges": []}
    mock_execute.assert_not_called()

# C. SUPER_ADMIN can request Case B graph.
@patch("app.services.graph_service.neo4j_client.execute")
def test_graph_super_admin(mock_execute):
    user = MagicMock(spec=User)
    user.role = "SUPER_ADMIN"
    get_graph(entity_id="p1", db=MagicMock(), user=user)

    assert mock_execute.called
    assert mock_execute.call_args[1]["is_super_admin"] == True

# D. Case A graph cannot expose Case B-only provenance through shared global entities.
@patch("app.services.matching_service.neo4j_client.execute")
def test_matching_provenance_shared_entity(mock_execute):
    mock_execute.return_value = []
    db = MagicMock(spec=Session)
    case_id = 1
    generate_case_entity_matches(db, case_id)

    # The matching_service now has EXACT constraints on record and candidate record being
    # connected via matching `case_id`s, proving Case B-only phones are not found.
    query = mock_execute.call_args[0][0]
    assert "EXISTS { MATCH (p2)<-[:MENTIONS]-(r2:Record {case_id: $case_id}) }" in query

# E. Empty authorized scope fails closed.
@patch("app.services.graph_service.neo4j_client.execute")
@patch("app.services.graph_service.get_authorized_case_ids")
def test_graph_empty_scope(mock_get_auth_cases, mock_execute):
    mock_get_auth_cases.return_value = set()
    user = MagicMock(spec=User)
    user.role = "INVESTIGATOR"

    result = get_graph(entity_id="p1", db=MagicMock(), user=user)
    assert result == {"nodes": [], "edges": []}
    mock_execute.assert_not_called()


@patch("app.services.graph_service.neo4j_client.execute")
@patch("app.services.graph_service.get_authorized_case_ids")
def test_graph_entity_traversal_uses_all_relationship_provenance(mock_get_auth_cases, mock_execute):
    mock_get_auth_cases.return_value = {1}
    user = MagicMock(spec=User)
    user.role = "INVESTIGATOR"

    get_graph(entity_id="person:a", db=MagicMock(), user=user)

    query = mock_execute.call_args.args[0]
    assert "ALL(rel IN relationships(path)" in query
    assert "rel.case_id IN $authorized_case_ids" in query
    assert "coalesce(rel.evidence_case_ids, [])" in query
    assert "r.case_id IN $authorized_case_ids" not in query
    assert mock_execute.call_args.kwargs["authorized_case_ids"] == [1]


@patch("app.services.graph_service.neo4j_client.execute")
@patch("app.services.graph_service.get_authorized_case_ids")
def test_graph_case_query_deduplicates_nodes_and_uses_target_label(mock_get_auth_cases, mock_execute):
    mock_get_auth_cases.return_value = {1}
    user = MagicMock(spec=User)
    user.role = "INVESTIGATOR"
    mock_execute.return_value = [{
        "nodes": [
            {"id": "person:a", "label": "A"},
            {"id": "person:a", "label": "A duplicate"},
            {"id": "phone:1", "label": "1"},
        ],
        "edges": [],
    }]

    result = get_graph(case_id=1, db=MagicMock(), user=user)

    query = mock_execute.call_args.args[0]
    assert "label:coalesce(m.name,m.value,m.entity_id)" in query
    assert "coalesce(m.name,n.value,n.entity_id)" not in query
    assert result["nodes"] == [
        {"id": "person:a", "label": "A duplicate"},
        {"id": "phone:1", "label": "1"},
    ]


@patch("app.services.matching_service.neo4j_client.execute")
def test_matching_signal_query_receives_case_id_and_scopes_phone_location(mock_execute):
    mock_execute.side_effect = [
        [{"source_id": "person:a", "candidate_id": "person:b"}],
        [{
            "shared_phones": 0,
            "shared_devices": 0,
            "shared_accounts": 0,
            "shared_locations": 0,
            "source_name": "A",
            "candidate_name": "B",
        }],
    ]
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None

    generate_case_entity_matches(db, 1)

    signal_call = mock_execute.call_args_list[1]
    query = signal_call.args[0]
    assert signal_call.kwargs["case_id"] == 1
    assert "spr:Record {case_id: $case_id}" in query
    assert "cpr:Record {case_id: $case_id}" in query
    assert "sp_record_rel.case_id = $case_id" in query
    assert "cp_record_rel.case_id = $case_id" in query
    assert "sl.case_id = $case_id" in query
    assert "cl.case_id = $case_id" in query
