__anchor__ = "tenant-profile"

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.tenant_profile.app.routers.profile import router
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("tenant-profile service starting", anchor="tenant-profile")
    yield
    logger.info("tenant-profile service stopped", anchor="tenant-profile")


app = FastAPI(
    title="pod-ft Tenant Profile",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(router, prefix="/api/v1")
