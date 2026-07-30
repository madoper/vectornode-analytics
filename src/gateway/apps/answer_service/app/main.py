__anchor__ = "answer-service"
# schema-ref: project-schema.yaml#/services/10

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.answer_service.app.routers import answer
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("answer-service starting", anchor="answer-service")
    yield
    logger.info("answer-service stopped", anchor="answer-service")


app = FastAPI(
    title="pod-ft Answer Service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(answer.router, prefix="/api/v1")
