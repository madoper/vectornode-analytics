__anchor__ = "export"
# schema-ref: project-schema.yaml#/services/14

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.export.app.routers import export
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("export starting", anchor="export")
    yield
    logger.info("export stopped", anchor="export")


app = FastAPI(
    title="pod-ft Export",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(export.router, prefix="/api/v1")
