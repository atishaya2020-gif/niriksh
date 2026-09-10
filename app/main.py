from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    cases,
    upload,
    graph,
    analytics,
    entities,
    records,
    dashboard,
    risk,
    alerts,
    network,
    search,
    evidence,
    matches,
)

from app.db.models import Base
from app.db.neo4j import neo4j_client
from app.db.postgres import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create any missing PostgreSQL tables.
    Base.metadata.create_all(bind=engine)

    # Create the default admin account if it does not exist.
    db = SessionLocal()

    try:
        auth.seed_admin(db)
    finally:
        db.close()

    yield

    # Close Neo4j connection on shutdown.
    neo4j_client.close()


app = FastAPI(
    title="Niriksh API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(
    auth.router,
    prefix="/api",
)

app.include_router(
    cases.router,
    prefix="/api",
)

app.include_router(
    upload.router,
    prefix="/api",
)

app.include_router(
    graph.router,
    prefix="/api",
)

app.include_router(
    analytics.router,
    prefix="/api",
)

app.include_router(
    entities.router,
    prefix="/api",
)

app.include_router(
    records.router,
    prefix="/api",
)

app.include_router(
    dashboard.router,
    prefix="/api",
)

app.include_router(
    risk.router,
    prefix="/api",
)

app.include_router(
    alerts.router,
    prefix="/api",
)

app.include_router(
    network.router,
    prefix="/api",
)

app.include_router(
    search.router,
    prefix="/api",
)

app.include_router(
    evidence.router,
    prefix="/api",
)

app.include_router(
    matches.router,
    prefix="/api",
)


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "ok",
        "service": "niriksh-backend",
    }