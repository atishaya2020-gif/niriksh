from app.db.neo4j import neo4j_client
from app.services.normalization import clean_text, normalize_identifier, normalize_name, normalize_phone


def merge_entity(label: str, entity_id: str, properties: dict):
    query = f"""
    MERGE (n:{label} {{entity_id: $entity_id}})
    SET n += $properties
    RETURN n.entity_id AS entity_id
    """
    return neo4j_client.execute(query, entity_id=entity_id, properties=properties)


def merge_record_relationship(record_node_id: str, entity_label: str, entity_id: str, relationship: str, **properties):
    query = f"""
    MATCH (r:Record {{entity_id: $record_node_id}}), (e:{entity_label} {{entity_id: $entity_id}})
    MERGE (r)-[rel:{relationship}]->(e)
    SET rel += $properties
    """
    neo4j_client.execute(query, record_node_id=record_node_id, entity_id=entity_id, properties=properties)


def merge_entity_relationship(
    source_label: str,
    source_id: str,
    relationship: str,
    target_label: str,
    target_id: str,
    **properties,
):
    query = f"""
    MATCH (source:{source_label} {{entity_id: $source_id}}), (target:{target_label} {{entity_id: $target_id}})
    MERGE (source)-[rel:{relationship}]->(target)
    SET rel += $properties
    """
    neo4j_client.execute(
        query,
        source_id=source_id,
        target_id=target_id,
        properties=properties,
    )


def canonical_name_key(value: str) -> str:
    return " ".join(value.lower().split())


def canonical_text_key(value) -> str | None:
    cleaned = clean_text(value)
    return " ".join(cleaned.lower().split()) if cleaned else None


def create_phone(record_id: str, case_id: int, value, role: str) -> str | None:
    phone = normalize_phone(value)
    if not phone:
        return None

    entity_id = f"phone:{phone}"
    merge_entity("Phone", entity_id, {"entity_id": entity_id, "value": phone})
    merge_record_relationship(
        record_id,
        "Phone",
        entity_id,
        "CONTAINS_PHONE",
        case_id=case_id,
        record_id=record_id,
        role=role,
        source_field={"contact": "contact_number", "caller": "caller_number", "callee": "callee_number"}[role],
    )
    return entity_id


def create_record_graph(row: dict, case_id: int):
    record_id = normalize_identifier(row.get("record_id"))
    if not record_id:
        return
    record_node_id = f"record:{case_id}:{record_id}"

    category = clean_text(row.get("category")) or "Unknown"
    merge_entity(
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
        merge_entity("Person", person_id, {"entity_id": person_id, "name": person, "identity_basis": "name_only"})
        merge_record_relationship(
            record_id,
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
        merge_entity("Location", location_id, {"entity_id": location_id, "name": city})
        merge_record_relationship(
            record_id,
            "Location",
            location_id,
            "AT_LOCATION",
            case_id=case_id,
            record_id=record_id,
            source_field="city",
        )
        if person_id:
            merge_entity_relationship(
                "Person",
                person_id,
                "ASSOCIATED_WITH",
                "Location",
                location_id,
                case_id=case_id,
                record_id=record_id,
            )

    contact_phone_id = create_phone(record_id, case_id, row.get("contact_number"), "contact")
    if person_id and contact_phone_id:
        merge_entity_relationship(
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
        caller_phone_id = create_phone(record_id, case_id, row.get("caller_number"), "caller")
        callee_phone_id = create_phone(record_id, case_id, row.get("callee_number"), "callee")
        imei = normalize_identifier(row.get("imei_number"))

        if caller_phone_id and callee_phone_id:
            merge_entity_relationship(
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
            merge_entity("Device", device_id, {"entity_id": device_id, "imei": imei, "value": imei})
            merge_record_relationship(
                record_id,
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
            merge_entity(
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
            merge_record_relationship(
                record_id,
                "BankAccount",
                account_id,
                "USES_ACCOUNT",
                case_id=case_id,
                record_id=record_id,
                source_field="account_number_masked",
            )

        if transaction:
            transaction_id = f"transaction:{transaction}"
            merge_entity(
                "Transaction",
                transaction_id,
                {"entity_id": transaction_id, "transaction_id": transaction, "value": transaction},
            )
            merge_record_relationship(
                record_id,
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
            merge_entity("Merchant", merchant_id, {"entity_id": merchant_id, "name": merchant})
            merge_record_relationship(
                record_id,
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
            merge_entity(
                "FIR",
                fir_id,
                {"entity_id": fir_id, "fir_number": fir, "value": fir, "status": clean_text(row.get("fir_status"))},
            )
            merge_record_relationship(
                record_id,
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
            merge_entity("PoliceStation", station_id, {"entity_id": station_id, "name": station})
            merge_record_relationship(
                record_id,
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
            merge_entity(
                "SocialAccount",
                social_id,
                {"entity_id": social_id, "platform": platform, "handle": handle, "value": handle},
            )
            merge_record_relationship(
                record_id,
                "SocialAccount",
                social_id,
                "INVOLVES_ACCOUNT",
                case_id=case_id,
                record_id=record_id,
                source_field="account_handle",
            )


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
    WHERE $case_id IS NULL OR n.case_id = $case_id OR m.case_id = $case_id OR r.case_id = $case_id
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
