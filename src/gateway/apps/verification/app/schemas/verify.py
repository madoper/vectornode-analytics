__anchor__ = "verification"
# schema-ref: project-schema.yaml#/services/9

from typing import Any

from pydantic import BaseModel


class CandidateFragment(BaseModel):
    fragment_id: str
    fragment_text: str
    citation_label: str | None = None
    tier: int = 1
    confidence: float = 1.0


class PrecheckRequest(BaseModel):
    question: str
    candidate_fragments: list[CandidateFragment]


class PrecheckResponse(BaseModel):
    allowed: bool
    reason_code: str | None = None
    fragment_count: int
    anchor: str = "verification"


class FinalizeRequest(BaseModel):
    question: str
    candidate_fragments: list[CandidateFragment]
    draft_summary: str | None = None
    citations: list[str] = []


class SufficiencyDecision(BaseModel):
    allowed: bool
    reason_code: str | None = None


class FinalizeResponse(BaseModel):
    allowed: bool
    reason_code: str | None = None
    verifier_status: str | None = None
    llm_verdict: dict[str, Any] | None = None
    anchor: str = "verification"
