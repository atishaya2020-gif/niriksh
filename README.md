# Niriksh

Niriksh is an investigation-support backend for SIH PS 26189. It accepts structured cybercrime records, stores source records per case, creates an evidence-oriented entity graph, and exposes APIs for graph exploration and investigative analytics. The current implementation is an MVP backend; it does not present NLP extraction or role-based authorization as complete features.

## Problem

Investigation data is often spread across FIRs, call records, bank transactions, social accounts, devices, and locations. Niriksh consolidates structured CSV evidence into case-scoped PostgreSQL records and a Neo4j graph so investigators can examine relationships, connected entities, and cross-case signals.

## Architecture

```text
Frontend (technology TBD)
          |
          v
       FastAPI
       /      \
      v        v
PostgreSQL    Neo4j
raw cases     entities and relationships
records       graph exploration and analytics
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component responsibilities and [docs/API.md](docs/API.md) for the API contract.

## Backend technology

- FastAPI and Python
- PostgreSQL with SQLAlchemy
- Neo4j graph database
- pandas-based CSV ingestion and Python normalization utilities
- spaCy dependency reserved for future unstructured-text extraction
- JWT authentication with an RBAC-ready user role field; endpoint-level RBAC enforcement is not yet implemented
- Frontend: TBD

## Prerequisites

- Python 3.12+
- Docker Desktop with Docker Compose

## Local setup

### 1. Configure environment variables

```powershell
copy .env.example .env
```

Set local credentials and a strong `SECRET_KEY` in `.env`. Do not commit this file.

### 2. Start PostgreSQL and Neo4j

```powershell
docker compose up -d
```

Docker Compose creates persistent named volumes for database data. Do not remove volumes when working with shared local data unless explicitly intended.

### 3. Create and activate a virtual environment

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 4. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 5. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

Swagger UI is available at `http://127.0.0.1:8000/docs`; the health endpoint is `http://127.0.0.1:8000/health`.

## Authentication

The application seeds a local demo administrator when the API starts if no `admin` user exists. Obtain a JWT through `POST /api/auth/login` and send it with protected requests:

```http
Authorization: Bearer <access_token>
```

Use a non-demo password and secret configuration for any shared or deployed environment.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Dataset and imports

The supplied full synthetic dataset belongs locally at `data/cybercrime_combined_dataset.csv`. It is intentionally ignored by Git so the repository remains lightweight and does not distribute potentially sensitive-looking records. Obtain it through the approved project-data channel, then place it at that path.

Small CSV fixtures remain versioned in `data/` for repeatable ingestion testing. Do not run a full import without team approval.

To import a dataset into the script's demo case:

```powershell
python scripts/import_dataset.py data/cybercrime_combined_dataset.csv
```

To inspect or apply the existing case-scoped uniqueness migration, use:

```powershell
python scripts/migrate_raw_records_case_scoped_unique.py
```

Only run migrations with an intentional database-change plan.

## Current API modules

- Authentication: login and current user
- Cases: create, list, and retrieve cases
- Ingestion: CSV upload by case
- Records: case-aware listing, filters, pagination, and lookup
- Entities: graph entity listing, detail, connections, and timeline
- Graph: case graph and entity-centered graph views
- Analytics: key people, communities, hidden links, suspicious patterns, and cross-case links
- System: health check

See [docs/API.md](docs/API.md) for paths, request shapes, and response structures.

## Team workflow

1. Pull the current branch and create a focused feature branch.
2. Keep backend changes scoped; do not reset databases, delete Docker volumes, or import the full dataset without approval.
3. Copy `.env.example` to a local `.env`; never commit credentials or tokens.
4. Run the unit suite before opening a pull request.
5. Update API documentation when a frontend-facing route or response changes.
6. Coordinate schema, ingestion, and graph-contract changes with frontend developers before merging.
