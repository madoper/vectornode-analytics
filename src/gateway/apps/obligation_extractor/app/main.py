__anchor__ = "obligation-extractor"
# schema-ref: project-schema.yaml#/services/6

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.obligation_extractor.app.routers import extract
from backend.apps.obligation_extractor.app.services.extractor_service import (
    ObligationExtractorService,
)
from backend.shared.logging import configure_logging, logger

extractor_service: ObligationExtractorService | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("obligation-extractor starting", anchor="obligation-extractor")
    global extractor_service
    extractor_service = ObligationExtractorService()
    yield
    logger.info("obligation-extractor stopped", anchor="obligation-extractor")


app = FastAPI(
    title="pod-ft Obligation Extractor",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(extract.router, prefix="/api/v1")
