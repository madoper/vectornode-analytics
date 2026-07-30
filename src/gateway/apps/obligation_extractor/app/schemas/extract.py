__anchor__ = "obligation-extractor"
# schema-ref: project-schema.yaml#/services/6

from typing import Any

from pydantic import BaseModel


class FragmentInput(BaseModel):
    fragment_id: str
    fragment_no: int
    fragment_text: str
    citation_label: str
    document_version_id: str | None = None


class ExtractObligationsRequest(BaseModel):
    document_id: str
    document_version_id: str
    fragments: list[FragmentInput]


class NormResponse(BaseModel):
    norm_id: str
    norm_code: str | None = None
    title: str | None = None
    norm_type: str
    summary: str | None = None
    confidence_score: float
    anchor: str = "obligation-extractor"


class ObligationResponse(BaseModel):
    obligation_id: str
    norm_id: str
    obligation_code: str | None = None
    subject_scope: dict[str, Any]
    required_actions: list[str]
    risk_level: str | None = None
    confidence_score: float
    source_fragment_ids: list[str]
    anchor: str = "obligation-extractor"


class ExtractObligationsResponse(BaseModel):
    document_id: str
    norms: list[NormResponse]
    obligations: list[ObligationResponse]
    norm_count: int
    obligation_count: int
    anchor: str = "obligation-extractor"
