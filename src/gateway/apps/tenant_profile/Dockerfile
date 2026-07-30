FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync --no-group dev --frozen
COPY backend/shared backend/shared
COPY backend/apps/tenant_profile backend/apps/tenant_profile
ENV PYTHONPATH=/app
EXPOSE 8022
CMD ["uv", "run", "uvicorn", "backend.apps.tenant_profile.app.main:app", "--host", "0.0.0.0", "--port", "8022"]
