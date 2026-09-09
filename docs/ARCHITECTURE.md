# Niriksh Architecture

```text
Frontend (technology TBD)
          |
          v
       FastAPI API layer
          |
    +-----+-----+
    v           v
PostgreSQL     Neo4j
    |           |
raw case       entities, relationships,
records        graph queries, analytics
    \           /
     \         /
      ingestion and graph services
```

## Frontend

The frontend has not been selected or implemented in this repository. It consumes the FastAPI REST endpoints, uses JWT bearer authentication, and renders case records, entity details, graph views, and analytics results.

## FastAPI API layer

The FastAPI application in `app/main.py` registers modules for authentication, cases, CSV upload, records, entities, graph queries, and analytics. Protected endpoints resolve the JWT user via `get_current_user`.

## PostgreSQL

PostgreSQL is the source of truth for application users, cases, and imported raw records.

- `users`: username, password hash, role, and active status.
- `cases`: investigation case metadata.
- `raw_records`: imported CSV rows, source payload, normalized category/date fields, and a case reference.

Raw record uniqueness is scoped to `(case_id, record_id)`. A record ID may appear in different cases, but a re-upload to the same case is skipped.

## Neo4j

Neo4j holds graph material derived from imported records. The graph service creates `Record` nodes and relevant evidence entities, including people, phones, locations, devices, bank accounts, transactions, merchants, FIRs, police stations, and social accounts when the structured row data supports them.

Relationship types capture the evidence linkage, such as `MENTIONS`, `CONTAINS_PHONE`, `OWNS_PHONE`, `AT_LOCATION`, `USES_DEVICE`, `USES_ACCOUNT`, and category-specific links.

Neo4j supports graph retrieval, entity exploration, and analytic queries. PostgreSQL remains authoritative for raw record content.

## Ingestion service

`app/services/ingestion.py` reads CSVs with pandas, removes known empty export columns, normalizes values, persists each accepted row in PostgreSQL, then invokes graph creation for successfully persisted rows.

The import result reports received, imported, skipped, failed, graph-failed, and error information. Graph failures are reported rather than silently ignored.

## Normalization

`app/services/normalization.py` prepares structured CSV values before persistence and graph construction. It handles null-like values, identifier canonicalization, scientific notation, Indian phone number variants, person names, and supported datetime formats.

## Graph service

`app/services/graph_service.py` maps normalized row fields into Neo4j entities and relationships. It also supplies the graph payload returned by graph endpoints. Record nodes use a case-scoped graph identity so the same raw record ID can safely appear in more than one case.

## Analytics

`app/api/analytics.py` queries Neo4j for investigative views:

- key people by graph connectivity
- person communities
- indirect person-to-person links
- suspicious reuse or connectivity patterns
- entities found across multiple cases

Results reflect the data currently present in Neo4j. Empty or partial graph data can result in empty analytics arrays.

## Configuration and deployment boundary

Runtime configuration is loaded from `.env` via `app/core/config.py`. The repository commits only `.env.example`; local credentials and secrets must remain in `.env` or another deployment secret store.

Docker Compose starts local PostgreSQL and Neo4j containers with persistent named volumes. Database contents are not committed to Git.
