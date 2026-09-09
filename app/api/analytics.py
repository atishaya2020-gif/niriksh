from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.db.models import User
from app.db.neo4j import neo4j_client

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/key-people")
def key_people(
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[r]-()
    WITH p, count(DISTINCT r) AS degree
    OPTIONAL MATCH (p)<-[:MENTIONS]-(record:Record)
    WITH p, degree, count(DISTINCT record) AS connected_records
    OPTIONAL MATCH (p)-[:OWNS_PHONE]->(phone:Phone)
    WITH p, degree, connected_records, count(DISTINCT phone) AS phones
    OPTIONAL MATCH (p)-[]-(entity)
    WHERE entity:BankAccount OR entity:Device
    WITH p, degree, connected_records, phones,
         count(DISTINCT entity) AS accounts_devices
    WITH p, degree, connected_records, phones, accounts_devices,
         degree + connected_records + phones + accounts_devices AS score
    RETURN p.entity_id AS person_id,
           p.name AS name,
           degree,
           connected_records,
           phones + accounts_devices AS connected_phones_accounts_devices,
           score,
           CASE
             WHEN score >= 10 THEN 'Highly connected across multiple records'
             WHEN score >= 5 THEN 'Connected to multiple entities'
             ELSE 'Limited graph connectivity'
           END AS reason
    ORDER BY score DESC, name
    LIMIT $limit
    """

    return neo4j_client.execute(query, limit=limit)


@router.get("/communities")
def communities(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
):
    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[*1..3]-(member)
    WHERE member:Person
    WITH p, collect(DISTINCT member.entity_id) + p.entity_id AS members
    WITH reduce(
        anchor = head(members),
        member IN members |
        CASE
          WHEN member < anchor THEN member
          ELSE anchor
        END
    ) AS community_id,
    members
    WITH community_id, collect(DISTINCT members) AS member_lists
    UNWIND member_lists AS member_list
    UNWIND member_list AS member
    RETURN community_id,
           collect(DISTINCT member) AS member_ids,
           count(DISTINCT member) AS member_count
    ORDER BY member_count DESC
    LIMIT $limit
    """

    return neo4j_client.execute(query, limit=limit)


@router.get("/hidden-links")
def hidden_links(
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
):
    query = """
    MATCH path=(a:Person)-[*2..3]-(b:Person)
    WHERE a.entity_id < b.entity_id
      AND NOT (a)-[:MENTIONS]-(b)

    WITH a, b, path,
         [node IN nodes(path) | labels(node)[0]] AS node_types

    RETURN DISTINCT
           a.entity_id AS source_person_id,
           a.name AS source_person,
           b.entity_id AS target_person_id,
           b.name AS target_person,
           [
             node IN nodes(path) |
             {
               id: node.entity_id,
               type: labels(node)[0],
               label: coalesce(node.name, node.value, node.entity_id)
             }
           ] AS path,
           length(path) AS hop_count,

           CASE
             WHEN 'Phone' IN node_types
                  AND 'Location' IN node_types
               THEN 'Both persons connect through the same phone and location.'
             WHEN 'Phone' IN node_types
               THEN 'Both persons connect through the same phone.'
             WHEN 'Location' IN node_types
               THEN 'Both persons connect through the same location.'
             WHEN 'BankAccount' IN node_types
               THEN 'Both persons connect through the same bank account.'
             WHEN 'Device' IN node_types
               THEN 'Both persons connect through the same device.'
             ELSE 'Both persons share graph evidence.'
           END AS explanation

    LIMIT $limit
    """

    return neo4j_client.execute(query, limit=limit)


@router.get("/suspicious-patterns")
def suspicious_patterns(
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
):
    query = """
    CALL {
      MATCH (phone:Phone)<-[:CONTAINS_PHONE]-(record:Record)
      WITH phone, count(DISTINCT record) AS record_count
      WHERE record_count > 1
      RETURN phone.entity_id AS entity_id,
             'Phone' AS entity_type,
             record_count AS evidence_count,
             'Phone appears in multiple records' AS reason

      UNION

      MATCH (caller:Phone)-[:CALLED]->(callee:Phone)
      WITH caller, count(DISTINCT callee) AS evidence_count
      WHERE evidence_count >= 3
      RETURN caller.entity_id AS entity_id,
             'Phone' AS entity_type,
             evidence_count,
             'Phone calls many different numbers' AS reason

      UNION

      MATCH (person:Person)-[:ASSOCIATED_WITH]->(location:Location)
      WITH person, count(DISTINCT location) AS evidence_count
      WHERE evidence_count > 1
      RETURN person.entity_id AS entity_id,
             'Person' AS entity_type,
             evidence_count,
             'Person is associated with multiple locations' AS reason

      UNION

      MATCH (account:BankAccount)<-[:USES_ACCOUNT]-(record:Record)
      WITH account, count(DISTINCT record) AS evidence_count
      WHERE evidence_count > 1
      RETURN account.entity_id AS entity_id,
             'BankAccount' AS entity_type,
             evidence_count,
             'Bank account appears in multiple records' AS reason

      UNION

      MATCH (record:Record)
      WHERE toLower(coalesce(record.fraud_flag, '')) IN ['yes', 'true']
      RETURN record.entity_id AS entity_id,
             'Record' AS entity_type,
             1 AS evidence_count,
             'Record is flagged as fraud' AS reason
    }

    RETURN entity_id,
           entity_type,
           evidence_count,
           reason
    ORDER BY evidence_count DESC, entity_id
    LIMIT $limit
    """

    return neo4j_client.execute(query, limit=limit)


@router.get("/cross-case-links")
def cross_case_links(
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
):
    """
    Identify entities that occur across multiple investigation cases.

    This is an analytical signal only. A cross-case association does not
    establish identity, guilt, or criminal involvement.
    """

    query = """
    MATCH (record:Record)-[]-(entity)
    WHERE entity:Phone
       OR entity:Device
       OR entity:BankAccount
       OR entity:SocialAccount
       OR entity:Person

    WITH entity,
         collect(DISTINCT record.case_id) AS cases,
         count(DISTINCT record) AS record_count

    WHERE size(cases) > 1

    WITH entity,
         cases,
         record_count,
         size(cases) AS case_count

    RETURN
        entity.entity_id AS entity_id,
        labels(entity)[0] AS entity_type,
        cases,
        case_count,
        record_count,

        CASE
          WHEN case_count >= 4
            THEN 0.90
          WHEN case_count = 3
            THEN 0.82
          ELSE 0.72
        END AS confidence,

        'Potential cross-case association: the same entity appears in multiple cases.'
            AS reason,

        'Potential Cross-Case Association'
            AS signal,

        true AS requires_human_verification,

        'Simulated analytical output'
            AS analysis_type

    ORDER BY case_count DESC, record_count DESC, entity_id
    LIMIT $limit
    """

    return neo4j_client.execute(query, limit=limit)