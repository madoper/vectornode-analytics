__anchor__ = "drafting"

from fastapi import APIRouter, HTTPException

from backend.apps.drafting.app.schemas.draft import (
    DraftRequest,
    DraftResponse,
)
from backend.apps.drafting.app.services.drafting_service import DraftingService

router = APIRouter(tags=["drafting"])
_service = DraftingService()


@router.post("/draft", response_model=DraftResponse)
async def generate_draft(payload: DraftRequest) -> DraftResponse:
    return await _service.generate_draft(
        document_type=payload.document_type,
        subject_type=payload.subject_type,
        context=payload.context,
    )


@router.get("/draft/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str) -> DraftResponse:
    result = await _service.get_draft(draft_id)
    if not result:
        raise HTTPException(status_code=404, detail="Draft not found")
    return result


@router.get("/drafts", response_model=list[DraftResponse])
async def list_drafts() -> list[DraftResponse]:
    return await _service.list_drafts()
