# Niriksh API

Base URL: `http://127.0.0.1:8000`

Interactive OpenAPI documentation is served at `/docs`.

## Authentication

All `/api` endpoints except `POST /api/auth/login` require a JWT bearer token.

```http
Authorization: Bearer <access_token>
```

### Login

`POST /api/auth/login`
Authentication: none

Request body:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response `200`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

Invalid credentials return `401`.

### Current user

`GET /api/auth/me`
Authentication: required

Response `200`:

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin"
}
```

## Cases

### Create case

`POST /api/cases`
Authentication: required

Request body:

```json
{
  "case_number": "CASE-001",
  "title": "Example investigation",
  "description": "Optional case description"
}
```

Response `200`:

```json
{
  "id": 1,
  "case_number": "CASE-001",
  "title": "Example investigation",
  "description": "Optional case description",
  "created_at": "2026-09-10T12:00:00Z"
}
```

### List cases

`GET /api/cases`
Authentication: required

Response `200`: array of case objects with the same shape as create-case responses, ordered by descending ID.

### Get case

`GET /api/cases/{case_id}`
Authentication: required

Path parameter: `case_id` (integer)

Response: a case object. The current implementation returns the database lookup result directly.

## CSV ingestion

### Upload CSV into a case

`POST /api/cases/{case_id}/upload-csv`
Authentication: required
Content type: `multipart/form-data`

Path parameter: `case_id` (integer)
Form field: `file` (CSV file; filename must end in `.csv`)

Response `200`:

```json
{
  "case_id": 2,
  "records_received": 10,
  "records_imported": 6,
  "records_skipped": 4,
  "records_failed": 0,
  "graph_failed": 0,
  "errors": [],
  "status": "completed"
}
```

`records_skipped` includes rows whose `record_id` already exists in the target case. The uniqueness rule is scoped to `(case_id, record_id)`, so a record ID in another case is not a duplicate. Non-CSV uploads return `400`; an unknown case returns `404`.

## Records

### List records

`GET /api/records`
Authentication: required

Optional query parameters:

- `case_id`: integer
- `category`: exact category string
- `record_status`: exact `payload.record_status` value
- `page`: integer, default `1`, minimum `1`
- `page_size`: integer, default `50`, range `1`–`200`

Response `200`:

```json
{
  "items": [
    {
      "id": 1,
      "record_id": "REC000440",
      "case_id": 1,
      "category": "Online FIR",
      "incident_datetime": "2025-06-26T08:00:00",
      "payload": {},
      "created_at": "2026-09-10T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

### Get record

`GET /api/records/{record_id}`
Authentication: required

Path parameter: `record_id` (string)
Optional query parameter: `case_id` (integer), recommended when the same record ID exists in multiple cases.

Response `200`: one record object with the same item shape above. Returns `404` if none is found.

## Entities

### List entities

`GET /api/entities`
Authentication: required

Optional query parameters:

- `entity_type`: graph label such as `Person`, `Phone`, or `Record`
- `search`: case-insensitive substring matched against name, value, or entity ID
- `limit`: integer, default `100`, range `1`–`500`

Response `200`: array of objects:

```json
[
  {
    "id": "person:anjali yadav",
    "type": "Person",
    "label": "Anjali Yadav",
    "properties": {
      "entity_id": "person:anjali yadav",
      "name": "Anjali Yadav"
    }
  }
]
```

### Get entity

`GET /api/entities/{entity_id}`
Authentication: required

Response `200`: one entity object with `id`, `type`, `label`, and `properties`. Returns `404` if the graph has no matching entity.

### Get entity connections

`GET /api/entities/{entity_id}/connections`
Authentication: required

Optional query parameter: `limit`, default `100`, range `1`–`500`.

Response `200`: array of connected entity objects:

```json
[
  {
    "id": "phone:8826000000",
    "type": "Phone",
    "label": "8826000000",
    "properties": {},
    "relationship_type": "OWNS_PHONE",
    "relationship_properties": {}
  }
]
```

### Get entity timeline

`GET /api/entities/{entity_id}/timeline`
Authentication: required

Response `200`: records connected to the entity, sorted by incident date descending:

```json
[
  {
    "record_id": "REC000440",
    "case_id": 1,
    "category": "Online FIR",
    "incident_datetime": "2025-06-26T08:00:00",
    "record_status": "Closed"
  }
]
```

## Graph

### Get graph

`GET /api/graph`
Authentication: required

Optional query parameter: `case_id` (integer). When supplied, graph relationships and nodes associated with that case are returned.

Response `200`:

```json
{
  "nodes": [
    {
      "id": "record:1:REC000440",
      "type": "Record",
      "label": "record:1:REC000440",
      "properties": {}
    }
  ],
  "edges": [
    {
      "id": "<neo4j-element-id>",
      "source": "record:1:REC000440",
      "target": "person:anjali yadav",
      "type": "MENTIONS",
      "properties": {}
    }
  ]
}
```

### Get entity-centered graph

`GET /api/graph/entity/{entity_id}`
Authentication: required

Query parameter: `depth`, default `2`, range `1`–`4`.

Response: the same `{ "nodes": [], "edges": [] }` graph structure.

## Analytics

All analytics endpoints require authentication.

### Key people

`GET /api/analytics/key-people`

Query parameter: `limit`, default `10`, range `1`–`100`.

Response objects include `person_id`, `name`, `degree`, `connected_records`, `connected_phones_accounts_devices`, `score`, and `reason`.

### Communities

`GET /api/analytics/communities`

Query parameter: `limit`, default `50`, range `1`–`200`.

Response objects include `community_id`, `member_ids`, and `member_count`.

### Hidden links

`GET /api/analytics/hidden-links`

Query parameter: `limit`, default `100`, range `1`–`500`.

Response objects include source/target person IDs and names, the graph `path`, `hop_count`, and an `explanation`.

### Suspicious patterns

`GET /api/analytics/suspicious-patterns`

Query parameter: `limit`, default `100`, range `1`–`500`.

Response objects include `entity_id`, `entity_type`, `evidence_count`, and `reason`.

### Cross-case links

`GET /api/analytics/cross-case-links`

Query parameter: `limit`, default `100`, range `1`–`500`.

Response objects include `entity_id`, `entity_type`, `cases`, `case_count`, and `reason`.

## System

### Health

`GET /health`
Authentication: none

Response `200`:

```json
{
  "status": "ok",
  "service": "niriksh-backend"
}
```
