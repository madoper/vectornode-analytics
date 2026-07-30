__anchor__ = "doc-check"
# schema-ref: project-schema.yaml#/services/12


from pydantic import BaseModel


class CheckRequest(BaseModel):
    tenant_id: str
    document_text: str
    document_title: str
    document_type: str = "internal_policy"
    subject_type: str | None = None


class Finding(BaseModel):
    finding_type: str
    summary: str
    obligation_id: str | None = None
    citation_label: str | None = None
    fragment_text: str | None = None
    confidence: float = 0.0


class ExportLink(BaseModel):
    format: str
    url: str
    label: str


class CheckResponse(BaseModel):
    job_id: str
    status: str
    total_fragments_found: int
    findings: list[Finding]
    coverage_summary: str
    created_at: str
    export_links: list[ExportLink] = []
    anchor: str = "doc-check"


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    result: CheckResponse | None = None
    error_message: str | None = None
    anchor: str = "doc-check"
