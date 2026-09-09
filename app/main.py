from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import auth, cases, upload, graph, analytics, entities, records
from app.db.models import Base
from app.db.neo4j import neo4j_client
from app.db.postgres import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        auth.seed_admin(db)
    finally:
        db.close()
    yield
    neo4j_client.close()


app = FastAPI(title="Niriksh API", version="0.1.0", lifespan=lifespan)
app.include_router(auth.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(entities.router, prefix="/api")
app.include_router(records.router, prefix="/api")


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "niriksh-backend"}
