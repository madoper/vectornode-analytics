# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --no-group dev --frozen

COPY backend/shared backend/shared
COPY backend/apps/verification backend/apps/verification

ENV PYTHONPATH=/app
EXPOSE 8010

CMD ["uv", "run", "uvicorn", "backend.apps.verification.app.main:app", "--host", "0.0.0.0", "--port", "8010"]
