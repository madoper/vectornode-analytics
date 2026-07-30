__anchor__ = "gateway"
# schema-ref: project-schema.yaml#/services/0/api/public

from fastapi import APIRouter
from pydantic import BaseModel

from backend.apps.gateway.app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


class VersionResponse(BaseModel):
    version: str = "0.5.0"
    name: str = "podft-rag-platform"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="gateway", anchor="gateway")


@router.get("/api/v1/health", response_model=HealthResponse)
async def api_health() -> HealthResponse:
    return HealthResponse(status="ok", service="gateway", version="0.5.0", anchor="gateway")


@router.get("/api/v1/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse()
