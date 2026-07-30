__anchor__ = "document-upload"

from fastapi import APIRouter, File, UploadFile

from backend.apps.document_upload.app.schemas.upload import UploadListResponse, UploadResponse
from backend.apps.document_upload.app.services.upload_service import UploadService

router = APIRouter(tags=["document-upload"])
_service = UploadService()


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    return await _service.upload(
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        content=content,
    )


@router.get("/documents", response_model=UploadListResponse)
async def list_documents() -> UploadListResponse:
    docs = await _service.list_documents()
    return UploadListResponse(documents=docs, total=len(docs))
