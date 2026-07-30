__anchor__ = "auth-billing"
# schema-ref: project-schema.yaml#/services/1

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.auth_billing.app.routers import auth
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("auth-billing starting", anchor="auth-billing")
    yield
    logger.info("auth-billing stopped", anchor="auth-billing")


app = FastAPI(
    title="pod-ft Auth & Billing",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
)

app.include_router(auth.router, prefix="/api/v1")
