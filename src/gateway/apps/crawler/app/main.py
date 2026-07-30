__anchor__ = "crawler"
# schema-ref: project-schema.yaml#/services/3

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.apps.crawler.app.routers import crawl
from backend.shared.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("crawler starting", anchor="crawler")
    yield
    logger.info("crawler stopped", anchor="crawler")


app = FastAPI(title="pod-ft Crawler", version="0.1.0", lifespan=lifespan, docs_url="/api/v1/docs")
app.include_router(crawl.router, prefix="/api/v1")
