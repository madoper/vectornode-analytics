__anchor__ = "workers"
# schema-ref: project-schema.yaml#/services/15

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.workers.app.routers import job
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("workers starting", anchor="workers")
    yield
    logger.info("workers stopped", anchor="workers")


app = FastAPI(
    title="pod-ft Workers",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(job.router, prefix="/api/v1")
