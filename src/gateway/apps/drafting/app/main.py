__anchor__ = "drafting"
# schema-ref: project-schema.yaml#/services/13

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.drafting.app.routers import draft
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("drafting starting", anchor="drafting")
    yield
    logger.info("drafting stopped", anchor="drafting")


app = FastAPI(
    title="pod-ft Drafting",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(draft.router, prefix="/api/v1")
