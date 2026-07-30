__anchor__ = "parser"
# schema-ref: project-schema.yaml#/services/4

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.parser.app.routers import parse
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("parser starting", anchor="parser")
    yield
    logger.info("parser stopped", anchor="parser")


app = FastAPI(title="pod-ft Parser", version="0.1.0", lifespan=lifespan, docs_url="/api/v1/docs")
app.include_router(parse.router, prefix="/api/v1")
