__anchor__ = "source-registry"
# schema-ref: project-schema.yaml#/services/2

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.source_registry.app.routers import sources
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("source-registry starting", anchor="source-registry")
    yield
    logger.info("source-registry stopped", anchor="source-registry")


app = FastAPI(
    title="pod-ft Source Registry",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)

app.include_router(sources.router, prefix="/api/v1")
