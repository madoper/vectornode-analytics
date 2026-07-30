__anchor__ = "retrieval"
# schema-ref: project-schema.yaml#/services/8

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.retrieval.app.routers import search
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("retrieval starting", anchor="retrieval")
    yield
    logger.info("retrieval stopped", anchor="retrieval")


app = FastAPI(
    title="pod-ft Retrieval",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(search.router, prefix="/api/v1")
