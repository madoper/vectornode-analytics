__anchor__ = "doc-check"
# schema-ref: project-schema.yaml#/services/12

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.doc_check.app.routers import check
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("doc-check starting", anchor="doc-check")
    yield
    logger.info("doc-check stopped", anchor="doc-check")


app = FastAPI(
    title="pod-ft Document Check",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(check.router, prefix="/api/v1")
