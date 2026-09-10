from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.db.models import EntityMatch
from app.db.neo4j import neo4j_client


def generate_case_entity_matches(db: Session, case_id: int) -> list[EntityMatch]:
    """
    Generate potential entity matches for a given case using candidate blocking.
    Blocks on:
    - Shared phone
    - Shared device (IMEI)
    - Shared bank account
    - Shared location / normalized name similarity
    Does NOT perform all-to-all comparisons. Prevents duplicate pairs.
    """
    query = """
    MATCH (r:Record {case_id: $case_id})--(p:Person)
    
    // Block 1: Shared phone
    OPTIONAL MATCH (p)-[:OWNS_PHONE]->(ph:Phone)<-[:OWNS_PHONE|CONTAINS_PHONE]-(p2:Person)
    WHERE p.entity_id < p2.entity_id

    // Block 2: Shared device
    OPTIONAL MATCH (p)-[:USES_DEVICE]->(d:Device)<-[:USES_DEVICE]-(p3:Person)
    WHERE p.entity_id < p3.entity_id

    // Block 3: Shared bank account
    OPTIONAL MATCH (p)-[:USES_ACCOUNT]->(acc:BankAccount)<-[:USES_ACCOUNT]-(p4:Person)
    WHERE p.entity_id < p4.entity_id

    WITH p, 
         collect(DISTINCT ph) AS phones, 
         collect(DISTINCT d) AS devices, 
         collect(DISTINCT acc) AS accounts,
         collect(DISTINCT p2) + collect(DISTINCT p3) + collect(DISTINCT p4) AS candidate_persons

    UNWIND candidate_persons AS candidate
    WHERE candidate IS NOT NULL AND p.entity_id <> candidate.entity_id

    RETURN DISTINCT
        p.entity_id AS source_id,
        p.name AS source_name,
        candidate.entity_id AS candidate_id,
        candidate.name AS candidate_name
    LIMIT 100
    """

    rows = neo4j_client.execute(query, case_id=case_id)
    created_matches = []

    for row in rows:
        source_id = row["source_id"]
        candidate_id = row["candidate_id"]

        # Ensure canonical ordering to prevent A/B vs B/A duplicates
        if source_id > candidate_id:
            source_id, candidate_id = candidate_id, source_id

        existing = (
            db.query(EntityMatch)
            .filter(
                EntityMatch.case_id == case_id,
                EntityMatch.source_entity_id == source_id,
                EntityMatch.candidate_entity_id == candidate_id,
            )
            .first()
        )

        if existing:
            continue

        # Evaluate signals between source and candidate
        signal_query = """
        MATCH (s:Person {entity_id: $source_id}), (c:Person {entity_id: $candidate_id})
        
        OPTIONAL MATCH (s)-[:OWNS_PHONE]->(ph:Phone)<-[:OWNS_PHONE|CONTAINS_PHONE]-(c)
        OPTIONAL MATCH (s)-[:USES_DEVICE]->(d:Device)<-[:USES_DEVICE]-(c)
        OPTIONAL MATCH (s)-[:USES_ACCOUNT]->(acc:BankAccount)<-[:USES_ACCOUNT]-(c)
        OPTIONAL MATCH (s)-[:ASSOCIATED_WITH]->(l:Location)<-[:ASSOCIATED_WITH]-(c)
        
        RETURN 
            count(DISTINCT ph) AS shared_phones,
            count(DISTINCT d) AS shared_devices,
            count(DISTINCT acc) AS shared_accounts,
            count(DISTINCT l) AS shared_locations,
            s.name AS source_name,
            c.name AS candidate_name
        """
        signal_rows = neo4j_client.execute(
            signal_query, source_id=source_id, candidate_id=candidate_id
        )

        if not signal_rows:
            continue

        sig = signal_rows[0]
        shared_phones = int(sig.get("shared_phones", 0))
        shared_devices = int(sig.get("shared_devices", 0))
        shared_accounts = int(sig.get("shared_accounts", 0))
        shared_locations = int(sig.get("shared_locations", 0))
        
        source_name = sig.get("source_name") or ""
        candidate_name = sig.get("candidate_name") or ""

        score = 0.0
        reasons = []
        signals = {
            "shared_phones": shared_phones,
            "shared_devices": shared_devices,
            "shared_accounts": shared_accounts,
            "shared_locations": shared_locations,
            "name_match": source_name.strip().lower() == candidate_name.strip().lower()
        }

        if shared_phones > 0:
            score += 40.0
            reasons.append(f"Shared phone identifier count: {shared_phones}")
        if shared_devices > 0:
            score += 30.0
            reasons.append(f"Shared device (IMEI) count: {shared_devices}")
        if shared_accounts > 0:
            score += 30.0
            reasons.append(f"Shared bank account count: {shared_accounts}")
        if shared_locations > 0:
            score += 15.0
            reasons.append(f"Shared location overlap count: {shared_locations}")

        if signals["name_match"] and source_name:
            score += 20.0
            reasons.append("Exact normalized name match")

        score = min(score, 100.0)
        confidence = round(min(0.50 + (score / 200.0), 0.95), 2)

        if not reasons:
            reasons.append("Potential associative overlap")

        match_record = EntityMatch(
            case_id=case_id,
            source_entity_id=source_id,
            candidate_entity_id=candidate_id,
            source_entity_type="Person",
            candidate_entity_type="Person",
            match_score=score,
            confidence=confidence,
            matching_factors={
                "reasons": reasons,
                "signals": signals,
            },
            status="PENDING_REVIEW",
        )

        db.add(match_record)
        created_matches.append(match_record)

    db.commit()
    return created_matches
