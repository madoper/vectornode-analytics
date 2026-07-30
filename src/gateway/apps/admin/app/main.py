__anchor__ = "admin"

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.admin.app.routers.admin import router
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("admin service starting", anchor="admin")
    yield
    logger.info("admin service stopped", anchor="admin")


app = FastAPI(
    title="pod-ft Admin",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(router, prefix="/api/v1")
