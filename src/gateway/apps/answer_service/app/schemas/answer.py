__anchor__ = "answer-service"
# schema-ref: project-schema.yaml#/services/10

from datetime import date

from pydantic import BaseModel, Field


class AnswerQuestionRequest(BaseModel):
    channel: str = "web"
    question: str = Field(min_length=5, max_length=8000)
    subject_type: str | None = None
    regulator: str | None = None
    as_of_date: date | None = None


class CitationDto(BaseModel):
    fragment_id: str
    document_title: str | None = None
    citation_label: str
    quote: str
    source_url: str | None = None
    version_effective_from: date | None = None
    confidence_score: float = 0.0


class AnswerDto(BaseModel):
    summary: str
    citations: list[CitationDto]
    applicability_explanation: list[str] = []
    llm_summary: str | None = None


class AnswerQuestionResponse(BaseModel):
    answer_session_id: str
    status: str  # "ok" | "refused"
    answer: AnswerDto | None = None
    reason_code: str | None = None
    evidence_count: int = 0
    verifier_status: str | None = None
    anchor: str = "answer-service"
