__anchor__ = "scheduler"
# schema-ref: project-schema.yaml#/services/14

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.scheduler.app.routers import schedule
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("scheduler starting", anchor="scheduler")
    yield
    logger.info("scheduler stopped", anchor="scheduler")


app = FastAPI(
    title="pod-ft Scheduler",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(schedule.router, prefix="/api/v1")
