__anchor__ = "changes"

from fastapi import APIRouter, HTTPException, Query

from backend.apps.changes.app.schemas.changes import (
    ChangesListResponse,
    VersionDiffResponse,
)
from backend.apps.changes.app.services.change_service import ChangeDetectionService

router = APIRouter(tags=["changes"])
_service = ChangeDetectionService()


@router.get("/changes", response_model=ChangesListResponse)
async def list_changes(limit: int = Query(50, ge=1, le=200)) -> ChangesListResponse:
    return await _service.list_changes(limit=limit)


@router.get("/changes/{document_id}/diff", response_model=VersionDiffResponse)
async def diff_versions(
    document_id: str,
    from_version_id: str = Query(..., description="Source version ID"),
    to_version_id: str = Query(..., description="Target version ID"),
) -> VersionDiffResponse:
    result = await _service.diff_versions(document_id, from_version_id, to_version_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document or versions not found")
    return result
