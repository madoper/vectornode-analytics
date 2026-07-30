__anchor__ = "versioning"
# schema-ref: project-schema.yaml#/services/5

from pydantic import BaseModel


class RegisterDocumentRequest(BaseModel):
    canonical_url: str
    document_title: str | None = None
    document_kind: str = "unknown"
    content_hash: str
    regulator_code: str | None = None


class RegisterDocumentResponse(BaseModel):
    document_id: str
    version_id: str
    is_new_version: bool
    version_label: str | None = None
    is_current: bool
    anchor: str = "versioning"


class DocumentVersionResponse(BaseModel):
    version_id: str
    version_label: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    is_current: bool
    content_hash: str
    anchor: str = "versioning"


class DocumentTimelineResponse(BaseModel):
    document_id: str
    title: str
    version_count: int
    versions: list[DocumentVersionResponse]
    anchor: str = "versioning"
