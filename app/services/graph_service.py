from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from app.db.neo4j import neo4j_client
from app.services.normalization import clean_text, normalize_identifier, normalize_name, normalize_phone


@dataclass(slots=True)
class BatchQueue:
    """Collects parameter rows per Cypher template and flushes them with UNWIND."""
    entity_rows_by_label: dict[str, list[dict]] = None
    record_rel_rows_by_key: dict[tuple[str, str], list[dict]] = None
    entity_rel_rows_by_key: dict[tuple[str, str, str], list[dict]] = None

    def __post_init__(self):
        self.entity_rows_by_label = {}
        self.record_rel_rows_by_key = {}
        self.entity_rel_rows_by_key = {}

    def queue_entity(self, label: str, entity_id: str, properties: dict):
        self.entity_rows_by_label.setdefault(label, []).append({"entity_id": entity_id, "properties": properties})

    def queue_record_rel(self, record_node_id: str, entity_label: str, entity_id: str,
                         relationship: str, properties: dict):
        key = (entity_label, relationship)
        self.record_rel_rows_by_key.setdefault(key, []).append({
            "record_node_id": record_node_id,
            "entity_id": entity_id,
            "properties": properties,
        })

    def queue_entity_rel(self, source_label: str, source_id: str, relationship: str,
                         target_label: str, target_id: str, properties: dict):
        key = (source_label, target_label, relationship)
        provenance = {
            "case_id": properties.get("case_id"),
            "record_id": properties.get("record_id"),
            "source_field": properties.get("source_field"),
        }
        self.entity_rel_rows_by_key.setdefault(key, []).append({
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties,
            "provenance": provenance,
        })

    def flush(self):
        for label, rows in self.entity_rows_by_label.items():
            neo4j_client.execute_write_batch(_entity_merge_cypher(label), rows)
        self.entity_rows_by_label.clear()

        for (entity_label, relationship), rows in self.record_rel_rows_by_key.items():
            neo4j_client.execute_write_batch(_record_rel_cypher(entity_label, relationship), rows)
        self.record_rel_rows_by_key.clear()

        for (source_label, target_label, relationship), rows in self.entity_rel_rows_by_key.items():
            neo4j_client.execute_write_batch(_entity_rel_cypher(source_label, target_label, relationship), rows)
        self.entity_rel_rows_by_key.clear()


def _entity_merge_cypher(label: str) -> str:
    return f"""
UNWIND $rows AS row
MERGE (n:{label} {{entity_id: row.entity_id}})
SET n += row.properties
"""

def _record_rel_cypher(entity_label: str, relationship: str) -> str:
    return f"""
UNWIND $rows AS row
MATCH (r:Record {{entity_id: row.record_node_id}}), (e:{entity_label} {{entity_id: row.entity_id}})
MERGE (r)-[rel:{relationship}]->(e)
SET rel += row.properties
"""

def _entity_rel_cypher(source_label: str, target_label: str, relationship: str) -> str:
    return f"""
UNWIND $rows AS row
MATCH (source:{source_label} {{entity_id: row.source_id}}), (target:{target_label} {{entity_id: row.target_id}})
MERGE (source)-[rel:{relationship}]->(target)
SET rel += row.properties
FOREACH (_ IN CASE WHEN row.provenance.record_id IS NULL THEN [] ELSE [1] END |
  SET rel.evidence_record_ids = coalesce(rel.evidence_record_ids, []) +
    CASE WHEN NOT row.provenance.record_id IN coalesce(rel.evidence_record_ids, [])
         THEN [row.provenance.record_id] ELSE [] END
)
FOREACH (_ IN CASE WHEN row.provenance.case_id IS NULL THEN [] ELSE [1] END |
  SET rel.evidence_case_ids = coalesce(rel.evidence_case_ids, []) +
    CASE WHEN NOT row.provenance.case_id IN coalesce(rel.evidence_case_ids, [])
         THEN [row.provenance.case_id] ELSE [] END
)
"""


class GraphBatch:
    """Batches graph write operations into bounded write transactions."""

    def __init__(self, batch_size: int = 200):
        self.batch_size = batch_size
        self._queued = 0
        self.queue = BatchQueue()
        self.entity_ids: set[str] = set()
        self.relationship_count = 0

    def maybe_flush(self):
        if self._queued >= self.batch_size:
            self.flush_all()

    def flush_all(self):
        self.queue.flush()
        self._queued = 0

    def _counted(self):
        self._queued += 1
        self.maybe_flush()

    def merge_entity(self, label: str, entity_id: str, properties: dict):
        self.entity_ids.add(entity_id)
        self.queue.queue_entity(label, entity_id, properties)
        self._counted()

    def merge_record_relationship(
        self,
        record_node_id: str,
        entity_label: str,
        entity_id: str,
        relationship: str,
        **properties,
    ):
        self.relationship_count += 1
        self.queue.queue_record_rel(record_node_id, entity_label, entity_id, relationship, properties)
        self._counted()

    def merge_entity_relationship(
        self,
        source_label: str,
        source_id: str,
        relationship: str,
        target_label: str,
        target_id: str,
        **properties,
    ):
        self.relationship_count += 1
        self.queue.queue_entity_rel(source_label, source_id, relationship, target_label, target_id, properties)
        self._counted()


def canonical_name_key(value: str) -> str:
    return " ".join(value.lower().split())


def canonical_text_key(value) -> str | None:
    cleaned = clean_text(value)
    return " ".join(cleaned.lower().split()) if cleaned else None


def create_phone(batch: GraphBatch, record_node_id: str, case_id: int, value, role: str) -> str | None:
    phone = normalize_phone(value)
    if not phone:
        return None

    entity_id = f"phone:{phone}"
    batch.merge_entity("Phone", entity_id, {"entity_id": entity_id, "value": phone})
    batch.merge_record_relationship(
        record_node_id,
        "Phone",
        entity_id,
        "CONTAINS_PHONE",
        case_id=case_id,
        record_id=record_node_id.split(":")[-1],
        role=role,
        source_field={"contact": "contact_number", "caller": "caller_number", "callee": "callee_number"}[role],
    )
    return entity_id


def create_record_graph(row: dict, case_id: int, batch: GraphBatch | None = None):
    record_id = normalize_identifier(row.get("record_id"))
    if not record_id:
        return
    record_node_id = f"record:{case_id}:{record_id}"

    own_batch = batch is None
    batch = batch or GraphBatch()

    category = clean_text(row.get("category")) or "Unknown"
    batch.merge_entity(
        "Record",
        record_node_id,
        {
            "entity_id": record_node_id,
            "record_id": record_id,
            "category": category,
            "case_id": case_id,
            "fraud_flag": clean_text(row.get("fraud_flag")),
            "transaction_amount_inr": clean_text(row.get("transaction_amount_inr")),
        },
    )

    person = normalize_name(row.get("person_name"))
    person_id = None
    if person:
        person_id = f"person:{canonical_name_key(person)}"
        batch.merge_entity("Person", person_id, {"entity_id": person_id, "name": person, "identity_basis": "name_only"})
        batch.merge_record_relationship(
            record_node_id,
            "Person",
            person_id,
            "MENTIONS",
            case_id=case_id,
            record_id=record_id,
            source_field="person_name",
        )

    city = clean_text(row.get("city"))
    if city:
        location_key = canonical_text_key(city)
        location_id = f"location:{location_key}"
        batch.merge_entity("Location", location_id, {"entity_id": location_id, "name": city})
        batch.merge_record_relationship(
            record_node_id,
            "Location",
            location_id,
            "AT_LOCATION",
            case_id=case_id,
            record_id=record_id,
            source_field="city",
        )
        if person_id:
            batch.merge_entity_relationship(
                "Person",
                person_id,
                "ASSOCIATED_WITH",
                "Location",
                location_id,
                case_id=case_id,
                record_id=record_id,
            )

    contact_phone_id = create_phone(batch, record_node_id, case_id, row.get("contact_number"), "contact")
    if person_id and contact_phone_id:
        batch.merge_entity_relationship(
            "Person",
            person_id,
            "OWNS_PHONE",
            "Phone",
            contact_phone_id,
            case_id=case_id,
            record_id=record_id,
            source_field="contact_number",
        )

    if category == "Call Data Record":
        caller_phone_id = create_phone(batch, record_node_id, case_id, row.get("caller_number"), "caller")
        callee_phone_id = create_phone(batch, record_node_id, case_id, row.get("callee_number"), "callee")
        imei = normalize_identifier(row.get("imei_number"))

        if caller_phone_id and callee_phone_id:
            batch.merge_entity_relationship(
                "Phone",
                caller_phone_id,
                "CALLED",
                "Phone",
                callee_phone_id,
                case_id=case_id,
                record_id=record_id,
                duration_sec=clean_text(row.get("call_duration_sec")),
                call_type=clean_text(row.get("call_type")),
            )

        if imei and imei.isdigit():
            device_id = f"device:{imei}"
            batch.merge_entity("Device", device_id, {"entity_id": device_id, "imei": imei, "value": imei})
            batch.merge_record_relationship(
                record_node_id,
                "Device",
                device_id,
                "USES_DEVICE",
                case_id=case_id,
                record_id=record_id,
                source_field="imei_number",
            )

    elif category == "Online Bank Transaction":
        account = normalize_identifier(row.get("account_number_masked"))
        bank_name = clean_text(row.get("bank_name"))
        transaction = normalize_identifier(row.get("transaction_id"))
        merchant = clean_text(row.get("merchant_name"))

        if account:
            account_key = canonical_text_key(account)
            if account.startswith("X") and bank_name:
                bank_key = canonical_text_key(bank_name)
                account_id = f"account:{bank_key}:{account_key}"
            else:
                account_id = f"account:{account_key}"
            batch.merge_entity(
                "BankAccount",
                account_id,
                {
                    "entity_id": account_id,
                    "value": account,
                    "masked": account,
                    "bank_name": bank_name,
                    "is_masked": account.startswith("X"),
                },
            )
            batch.merge_record_relationship(
                record_node_id,
                "BankAccount",
                account_id,
                "USES_ACCOUNT",
                case_id=case_id,
                record_id=record_id,
                source_field="account_number_masked",
            )

        if transaction:
            transaction_id = f"transaction:{transaction}"
            batch.merge_entity(
                "Transaction",
                transaction_id,
                {"entity_id": transaction_id, "transaction_id": transaction, "value": transaction},
            )
            batch.merge_record_relationship(
                record_node_id,
                "Transaction",
                transaction_id,
                "HAS_TRANSACTION",
                case_id=case_id,
                record_id=record_id,
                source_field="transaction_id",
            )

        if merchant:
            merchant_key = canonical_text_key(merchant)
            merchant_id = f"merchant:{merchant_key}"
            batch.merge_entity("Merchant", merchant_id, {"entity_id": merchant_id, "name": merchant})
            batch.merge_record_relationship(
                record_node_id,
                "Merchant",
                merchant_id,
                "AT_MERCHANT",
                case_id=case_id,
                record_id=record_id,
                source_field="merchant_name",
            )

    elif category == "Online FIR":
        fir = normalize_identifier(row.get("fir_number"))
        station = clean_text(row.get("police_station"))

        if fir:
            fir_id = f"fir:{fir}"
            batch.merge_entity(
                "FIR",
                fir_id,
                {"entity_id": fir_id, "fir_number": fir, "value": fir, "status": clean_text(row.get("fir_status"))},
            )
            batch.merge_record_relationship(
                record_node_id,
                "FIR",
                fir_id,
                "REPRESENTS",
                case_id=case_id,
                record_id=record_id,
                source_field="fir_number",
            )

        if station:
            station_key = canonical_text_key(station)
            station_id = f"station:{station_key}"
            batch.merge_entity("PoliceStation", station_id, {"entity_id": station_id, "name": station})
            batch.merge_record_relationship(
                record_node_id,
                "PoliceStation",
                station_id,
                "FILED_AT",
                case_id=case_id,
                record_id=record_id,
                source_field="police_station",
            )

    elif category == "Social Media Theft":
        platform = clean_text(row.get("platform_name"))
        handle = normalize_identifier(row.get("account_handle"))
        if handle:
            platform_key = canonical_text_key(platform) if platform else "unknown"
            social_id = f"social:{platform_key}:{handle.lower()}"
            batch.merge_entity(
                "SocialAccount",
                social_id,
                {"entity_id": social_id, "platform": platform, "handle": handle, "value": handle},
            )
            batch.merge_record_relationship(
                record_node_id,
                "SocialAccount",
                social_id,
                "INVOLVES_ACCOUNT",
                case_id=case_id,
                record_id=record_id,
                source_field="account_handle",
            )

    if own_batch:
        batch.flush_all()


def import_csv_batch(rows: list[dict], case_id: int, batch_size: int = 200) -> dict:
    batch = GraphBatch(batch_size=batch_size)
    for row in rows:
        create_record_graph(row, case_id, batch)
    batch.flush_all()
    return {
        "entities_extracted": len(batch.entity_ids),
        "relationships_detected": batch.relationship_count,
        "records_projected": len(rows),
    }


def get_graph(case_id: int | None = None, entity_id: str | None = None, depth: int = 2):
    if entity_id:
        query = """
        MATCH path=(center {entity_id:$entity_id})-[*0..4]-(node)
        WHERE length(path) <= $depth
        WITH collect(DISTINCT center) + collect(DISTINCT node) AS graph_nodes,
             collect(DISTINCT relationships(path)) AS relationship_lists
        UNWIND graph_nodes AS n
        WITH collect(DISTINCT n) AS nodes, relationship_lists
        UNWIND relationship_lists AS relationship_list
        UNWIND relationship_list AS r
        RETURN
          [n IN nodes | {id:n.entity_id, type:labels(n)[0], label:coalesce(n.name,n.value,n.entity_id), properties:properties(n)}] AS nodes,
          collect(DISTINCT {id:elementId(r), source:startNode(r).entity_id, target:endNode(r).entity_id, type:type(r), properties:properties(r)}) AS edges
        """
        rows = neo4j_client.execute(query, entity_id=entity_id, depth=depth)
        return rows[0] if rows else {"nodes": [], "edges": []}

    query = """
    MATCH (n)-[r]->(m)
    WHERE ($case_id IS NULL OR n.case_id = $case_id OR m.case_id = $case_id OR r.case_id = $case_id)
      AND type(r) <> 'MATCHED_WITH'
    RETURN collect(DISTINCT {id:n.entity_id, type:labels(n)[0], label:coalesce(n.name,n.value,n.entity_id), properties:properties(n)}) +
           collect(DISTINCT {id:m.entity_id, type:labels(m)[0], label:coalesce(m.name,m.value,m.entity_id), properties:properties(m)}) AS nodes,
           collect(DISTINCT {id:elementId(r), source:n.entity_id, target:m.entity_id, type:type(r), properties:properties(r)}) AS edges
    """
    rows = neo4j_client.execute(query, case_id=case_id)
    if not rows:
        return {"nodes": [], "edges": []}
    result = rows[0]
    result["nodes"] = list({node["id"]: node for node in result["nodes"]}.values())
    return result