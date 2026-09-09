from neo4j import GraphDatabase
from app.core.config import settings


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def close(self):
        self.driver.close()

    def execute(self, query: str, **params):
        with self.driver.session() as session:
            return session.run(query, **params).data()

    def execute_write_batch(self, query: str, rows: list[dict]):
        if not rows:
            return
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(query, rows=rows).consume())


neo4j_client = Neo4jClient()