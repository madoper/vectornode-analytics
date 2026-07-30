__anchor__ = "gateway"
# schema-ref: project-schema.yaml#/services/0

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from backend.apps.admin.app.routers.admin import router as admin_router
from backend.apps.answer_service.app.routers.answer import router as answer_router
from backend.apps.auth_billing.app.routers.auth import router as auth_router
from backend.apps.changes.app.routers.changes import router as changes_router
from backend.apps.chat.app.routers.chat import router as chat_router
from backend.apps.crawler.app.routers.crawl import router as crawl_router
from backend.apps.doc_check.app.routers.check import router as check_router
from backend.apps.document_upload.app.routers.upload import router as upload_router
from backend.apps.drafting.app.routers.draft import router as draft_router
from backend.apps.export.app.routers.export import router as export_router
from backend.apps.gateway.app.routers import health
from backend.apps.gateway.app.routers.analytics import router as analytics_router
from backend.apps.graph_service.app.routers.graph import router as graph_router
from backend.apps.obligation_extractor.app.routers.extract import router as extract_router
from backend.apps.parser.app.routers.parse import router as parse_router
from backend.apps.retrieval.app.routers.search import router as search_router
from backend.apps.scheduler.app.routers.schedule import router as schedule_router
from backend.apps.source_registry.app.routers.sources import router as sources_router
from backend.apps.tenant_profile.app.routers.profile import router as tenant_profile_router
from backend.apps.vector_indexer.app.routers.index import router as index_router
from backend.apps.verification.app.routers.verify import router as verify_router
from backend.apps.versioning.app.routers.version import router as version_router
from backend.apps.workers.app.routers.job import router as job_router
from backend.shared.db.redis import redis_client
from backend.shared.idempotency import IdempotencyKeyMiddleware
from backend.shared.logging import RequestLoggingMiddleware, configure_logging, logger
from backend.shared.metrics import MetricsMiddleware, metrics_endpoint
from backend.shared.rate_limiter import RateLimitMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("gateway starting", anchor="gateway")
    await redis_client.connect()

    # Restore BM25 from disk
    try:
        from backend.apps.retrieval.app.services.retrieval_service import RetrievalService
        if RetrievalService.load_bm25():
            logger.info("gateway: BM25 index restored from disk (%d fragments)", RetrievalService._shared._total_docs)
    except Exception:
        pass

    # Seed regulatory fragments (only if BM25 not restored)
    try:
        from backend.shared.data.seed_fragments import ALL_SEED_FRAGMENTS
        retrieval = RetrievalService()
        seed_count = 0
        try:
            seed_count = await asyncio.wait_for(
                retrieval.index_fragments(ALL_SEED_FRAGMENTS), timeout=10
            )
        except TimeoutError:
            logger.warning("gateway: seed timed out (10s)")
        logger.info("gateway: seeded %d regulatory fragments", seed_count)
        qdrant_count = 0
        try:
            qdrant_count = await asyncio.wait_for(
                retrieval.load_from_qdrant(), timeout=10
            )
        except TimeoutError:
            logger.warning("gateway: Qdrant restore timed out (10s), skipping")
        if qdrant_count > 0:
            logger.info("gateway: restored %d fragments from Qdrant", qdrant_count)
    except Exception as exc:
        logger.warning("gateway: seed/restore failed: %s", exc)
    yield
    await redis_client.disconnect()
    logger.info("gateway stopped", anchor="gateway")


app = FastAPI(
    title="pod-ft Gateway",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

app.include_router(health.router)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/api/v1/docs")


app.include_router(auth_router, prefix="/api/v1")
app.include_router(schedule_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")
app.include_router(crawl_router, prefix="/api/v1")
app.include_router(parse_router, prefix="/api/v1")
app.include_router(version_router, prefix="/api/v1")
app.include_router(extract_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(verify_router, prefix="/api/v1")
app.include_router(answer_router, prefix="/api/v1")
app.include_router(index_router, prefix="/api/v1")
app.include_router(check_router, prefix="/api/v1")
app.include_router(draft_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(changes_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(tenant_profile_router, prefix="/api/v1")
app.include_router(analytics_router)


@app.get("/metrics")
async def metrics() -> Response:
    data = await metrics_endpoint()
    return Response(content=data, media_type="text/plain")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(IdempotencyKeyMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_sec=60)  # type: ignore[arg-type]
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)


