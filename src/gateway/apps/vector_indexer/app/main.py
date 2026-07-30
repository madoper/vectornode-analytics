__anchor__ = "vector-indexer"
# schema-ref: project-schema.yaml#/services/8

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.vector_indexer.app.routers import index
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("vector-indexer starting", anchor="vector-indexer")
    yield
    logger.info("vector-indexer stopped", anchor="vector-indexer")


app = FastAPI(
    title="pod-ft Vector Indexer",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(index.router, prefix="/api/v1")
