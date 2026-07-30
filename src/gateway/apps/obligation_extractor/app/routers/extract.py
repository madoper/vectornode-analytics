__anchor__ = "obligation-extractor"
# schema-ref: project-schema.yaml#/services/6

from fastapi import APIRouter, HTTPException

from backend.apps.obligation_extractor.app.schemas.extract import (
    ExtractObligationsRequest,
    ExtractObligationsResponse,
    NormResponse,
    ObligationResponse,
)
from backend.apps.obligation_extractor.app.services.extractor_service import (
    ObligationExtractorService,
)

router = APIRouter(tags=["obligations"])
_service = ObligationExtractorService()


@router.post("/extract", response_model=ExtractObligationsResponse)
async def extract_obligations(payload: ExtractObligationsRequest) -> ExtractObligationsResponse:
    result = await _service.extract(
        document_id=payload.document_id,
        document_version_id=payload.document_version_id,
        fragments=[f.model_dump() for f in payload.fragments],
    )
    return ExtractObligationsResponse(
        document_id=result["document_id"],
        norms=[NormResponse(**n) for n in result["norms"]],
        obligations=[ObligationResponse(**o) for o in result["obligations"]],
        norm_count=result["norm_count"],
        obligation_count=result["obligation_count"],
        anchor="obligation-extractor",
    )


@router.get("/norms", response_model=list[NormResponse])
async def list_norms() -> list[NormResponse]:
    norms = await _service.list_norms()
    return [NormResponse(**n) for n in norms]


@router.get("/norms/{norm_id}/obligations", response_model=list[ObligationResponse])
async def get_norm_obligations(norm_id: str) -> list[ObligationResponse]:
    obligations = await _service.get_obligations_by_norm(norm_id)
    if not obligations:
        raise HTTPException(status_code=404, detail="Norm not found")
    return [ObligationResponse(**o) for o in obligations]


@router.get("/obligations", response_model=list[ObligationResponse])
async def list_obligations() -> list[ObligationResponse]:
    obligations = await _service.list_obligations()
    return [ObligationResponse(**o) for o in obligations]
