__anchor__ = "verification"
# schema-ref: project-schema.yaml#/services/9

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.verification.app.routers import verify
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("verification starting", anchor="verification")
    yield
    logger.info("verification stopped", anchor="verification")


app = FastAPI(
    title="pod-ft Verification",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)
app.include_router(verify.router, prefix="/api/v1")
