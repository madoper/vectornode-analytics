FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/shared backend/shared
COPY backend/apps/admin backend/apps/admin

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.apps.admin.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
