__anchor__ = "versioning"
# schema-ref: project-schema.yaml#/services/5

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.versioning.app.routers import version
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("versioning starting", anchor="versioning")
    yield
    logger.info("versioning stopped", anchor="versioning")


app = FastAPI(
    title="pod-ft Versioning",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(version.router, prefix="/api/v1")
