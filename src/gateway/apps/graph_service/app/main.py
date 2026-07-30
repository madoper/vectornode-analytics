__anchor__ = "graph-service"
# schema-ref: project-schema.yaml#/services/7

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.graph_service.app.routers import graph
from backend.apps.graph_service.app.services.graph_store import GraphStore
from backend.shared.db.neo4j import Neo4jClient
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("graph-service starting", anchor="graph-service")
    neo4j = Neo4jClient()
    await neo4j.connect()
    graph.set_store(GraphStore(neo4j=neo4j))
    yield
    await neo4j.close()
    logger.info("graph-service stopped", anchor="graph-service")


app = FastAPI(
    title="pod-ft Graph Service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(graph.router, prefix="/api/v1")
