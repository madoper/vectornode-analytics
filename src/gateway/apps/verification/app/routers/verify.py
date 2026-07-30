__anchor__ = "verification"
# schema-ref: project-schema.yaml#/services/9

from fastapi import APIRouter

from backend.apps.verification.app.schemas.verify import (
    FinalizeRequest,
    FinalizeResponse,
    PrecheckRequest,
    PrecheckResponse,
)
from backend.apps.verification.app.services.llm_verifier import LlmVerifier
from backend.apps.verification.app.services.sufficiency_policy import SufficiencyPolicy

router = APIRouter(tags=["verification"])
_policy = SufficiencyPolicy()
_llm_verifier = LlmVerifier()


@router.post("/precheck", response_model=PrecheckResponse)
async def precheck(payload: PrecheckRequest) -> PrecheckResponse:
    decision = _policy.evaluate_fragments(
        [f.model_dump() for f in payload.candidate_fragments]
    )
    return PrecheckResponse(
        allowed=decision.allowed,
        reason_code=decision.reason_code,
        fragment_count=len(payload.candidate_fragments),
        anchor="verification",
    )


@router.post("/finalize", response_model=FinalizeResponse)
async def finalize_verification(payload: FinalizeRequest) -> FinalizeResponse:
    fragment_decision = _policy.evaluate_fragments(
        [f.model_dump() for f in payload.candidate_fragments]
    )
    draft_decision = _policy.evaluate_draft(
        draft_summary=payload.draft_summary,
        citations=payload.citations,
    )

    # Rule engine has priority
    if not fragment_decision.allowed:
        return FinalizeResponse(
            allowed=False,
            reason_code=fragment_decision.reason_code,
            verifier_status="rejected_by_rules",
            llm_verdict=None,
            anchor="verification",
        )
    if not draft_decision.allowed:
        return FinalizeResponse(
            allowed=False,
            reason_code=draft_decision.reason_code,
            verifier_status="rejected_by_rules",
            llm_verdict=None,
            anchor="verification",
        )

    # Rules pass → optional LLM verifier
    llm_result = await _llm_verifier.verify(
        question=payload.question,
        fragments=[f.model_dump() for f in payload.candidate_fragments],
        draft_summary=payload.draft_summary,
    )

    if not llm_result.get("passed", True):
        return FinalizeResponse(
            allowed=False,
            reason_code=llm_result.get("reason", "llm_rejected"),
            verifier_status="rejected_by_llm",
            llm_verdict=llm_result,
            anchor="verification",
        )

    return FinalizeResponse(
        allowed=True,
        verifier_status="approved",
        llm_verdict=llm_result,
        anchor="verification",
    )
