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


neo4j_client = Neo4jClient()
