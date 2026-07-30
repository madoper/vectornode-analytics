__anchor__ = "versioning"
# schema-ref: project-schema.yaml#/services/5

from fastapi import APIRouter, HTTPException

from backend.apps.versioning.app.schemas.version import (
    DocumentTimelineResponse,
    DocumentVersionResponse,
    RegisterDocumentRequest,
    RegisterDocumentResponse,
)
from backend.apps.versioning.app.services.versioning_service import VersioningService

router = APIRouter(tags=["versioning"])
_versioning_service = VersioningService()


@router.post("/documents/register", status_code=201, response_model=RegisterDocumentResponse)
async def register_document(payload: RegisterDocumentRequest) -> RegisterDocumentResponse:
    result = await _versioning_service.register_document(
        canonical_url=payload.canonical_url,
        document_title=payload.document_title,
        document_kind=payload.document_kind,
        content_hash=payload.content_hash,
        regulator_code=payload.regulator_code,
    )
    return RegisterDocumentResponse(
        document_id=result["document_id"],
        version_id=result["version_id"],
        is_new_version=result["is_new_version"],
        version_label=result.get("version_label"),
        is_current=result["is_current"],
        anchor="versioning",
    )


@router.get("/documents/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_versions(document_id: str) -> list[DocumentVersionResponse]:
    versions = await _versioning_service.list_versions(document_id)
    return [
        DocumentVersionResponse(
            version_id=v["id"],
            version_label=v.get("version_label"),
            effective_from=v.get("effective_from"),
            effective_to=v.get("effective_to"),
            is_current=v["is_current"],
            content_hash=v["content_hash"],
            anchor="versioning",
        )
        for v in versions
    ]


@router.get("/documents/{document_id}/timeline", response_model=DocumentTimelineResponse)
async def get_timeline(document_id: str) -> DocumentTimelineResponse:
    doc = await _versioning_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    versions = await _versioning_service.list_versions(document_id)
    return DocumentTimelineResponse(
        document_id=document_id,
        title=doc["title"],
        version_count=len(versions),
        versions=[
            DocumentVersionResponse(
                version_id=v["id"],
                version_label=v.get("version_label"),
                effective_from=v.get("effective_from"),
                effective_to=v.get("effective_to"),
                is_current=v["is_current"],
                content_hash=v["content_hash"],
                anchor="versioning",
            )
            for v in versions
        ],
        anchor="versioning",
    )
