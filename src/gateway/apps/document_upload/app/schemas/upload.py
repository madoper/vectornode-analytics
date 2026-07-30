__anchor__ = "document-upload"

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str = "uploaded"
    anchor: str = "document-upload"


class UploadListResponse(BaseModel):
    documents: list[UploadResponse]
    total: int
    anchor: str = "document-upload"
