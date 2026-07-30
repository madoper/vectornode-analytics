# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --no-group dev --frozen

COPY backend/shared backend/shared
COPY backend/apps/gateway backend/apps/gateway
COPY backend/apps/auth_billing backend/apps/auth_billing
COPY backend/apps/source_registry backend/apps/source_registry
COPY backend/apps/tenant_profile backend/apps/tenant_profile
COPY backend/apps/chat backend/apps/chat
COPY backend/apps/crawler backend/apps/crawler
COPY backend/apps/parser backend/apps/parser
COPY backend/apps/versioning backend/apps/versioning
COPY backend/apps/obligation_extractor backend/apps/obligation_extractor
COPY backend/apps/graph_service backend/apps/graph_service
COPY backend/apps/retrieval backend/apps/retrieval
COPY backend/apps/verification backend/apps/verification
COPY backend/apps/admin backend/apps/admin
COPY backend/apps/answer_service backend/apps/answer_service
COPY backend/apps/vector_indexer backend/apps/vector_indexer
COPY backend/apps/doc_check backend/apps/doc_check
COPY backend/apps/document_upload backend/apps/document_upload
COPY backend/apps/changes backend/apps/changes
COPY backend/apps/drafting backend/apps/drafting
COPY backend/apps/export backend/apps/export
COPY backend/apps/scheduler backend/apps/scheduler
COPY backend/apps/workers backend/apps/workers

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.apps.gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
