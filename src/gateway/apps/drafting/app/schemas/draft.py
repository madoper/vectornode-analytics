__anchor__ = "drafting"
# schema-ref: project-schema.yaml#/services/13

from pydantic import BaseModel


class DraftRequest(BaseModel):
    document_type: str
    subject_type: str | None = None
    context: str | None = None


class DraftSection(BaseModel):
    title: str
    content: str
    citations: list[str] = []


class DraftResponse(BaseModel):
    draft_id: str
    document_type: str
    title: str
    sections: list[DraftSection]
    summary: str
    anchor: str = "drafting"
