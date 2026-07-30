__anchor__ = "models"
# schema-ref: project-schema.yaml#/shared_modules/5

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class FragmentDto(BaseModel):
    fragment_id: UUID
    document_version_id: UUID
    fragment_no: int
    section_path: str | None = None
    paragraph_label: str | None = None
    page_no: int | None = None
    fragment_text: str
    canonical_text: str
    token_count: int | None = None
    extraction_confidence: float | None = None
    citation_label: str
    fragment_hash: str


class DocumentVersionDto(BaseModel):
    version_id: UUID
    document_id: UUID
    version_label: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    content_hash: str
    is_current: bool = True


class CrawlResultDto(BaseModel):
    result_id: UUID
    url: str
    content_type: str
    blob_key: str
    checksum: str
    discovered_at: datetime


class ParsedDocumentDto(BaseModel):
    document_identity: dict[str, str]
    text_blob_key: str
    fragments: list[FragmentDto]
