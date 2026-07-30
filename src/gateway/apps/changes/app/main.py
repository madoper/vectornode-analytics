__anchor__ = "changes"

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.changes.app.routers.changes import router
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("changes service starting", anchor="changes")
    yield
    logger.info("changes service stopped", anchor="changes")


app = FastAPI(
    title="pod-ft Changes",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(router, prefix="/api/v1")
