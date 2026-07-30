__anchor__ = "export"
# schema-ref: project-schema.yaml#/services/14

from fastapi import APIRouter

from backend.apps.export.app.schemas.export import ExportRequest, ExportResponse
from backend.apps.export.app.services.export_service import ExportService

router = APIRouter(tags=["export"])
_service = ExportService()


@router.post("/export", response_model=ExportResponse)
async def generate_export(payload: ExportRequest) -> ExportResponse:
    return await _service.export(payload)
