__anchor__ = "admin"

from fastapi import APIRouter

from backend.apps.admin.app.schemas.admin import (
    BlockListResponse,
    BlockRequest,
    BlockResponse,
    UnblockResponse,
)
from backend.apps.admin.app.services.admin_service import AdminService

router = APIRouter(tags=["admin"])
_service = AdminService()


@router.post("/admin/documents/{document_id}/block", response_model=BlockResponse)
async def block_document(document_id: str, payload: BlockRequest) -> BlockResponse:
    return await _service.block_document(
        target_id=document_id,
        reason=payload.reason,
        created_by=payload.created_by,
    )


@router.post("/admin/norms/{norm_id}/block", response_model=BlockResponse)
async def block_norm(norm_id: str, payload: BlockRequest) -> BlockResponse:
    return await _service.block_norm(
        target_id=norm_id,
        reason=payload.reason,
        created_by=payload.created_by,
    )


@router.post("/admin/unblock/{target_id}", response_model=UnblockResponse)
async def unblock(target_id: str) -> UnblockResponse:
    return await _service.unblock(target_id=target_id)


@router.get("/admin/blocks", response_model=BlockListResponse)
async def list_blocks() -> BlockListResponse:
    return await _service.list_blocks()
