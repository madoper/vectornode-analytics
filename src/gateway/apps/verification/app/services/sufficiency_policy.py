__anchor__ = "verification"
# schema-ref: project-schema.yaml#/services/9
# schema-ref: production-tech-project-podft-rag-dev-spec.md#/13.3 Rule engine policy object

from typing import Any

from backend.apps.verification.app.schemas.verify import SufficiencyDecision


class SufficiencyPolicy:
    """Rule engine for evidence sufficiency.

    Implements the policy object from spec section 13.3.
    Rule engine has priority over verifier LLM.
    """

    min_fragments = 2
    max_low_confidence_share = 0.30
    min_confidence_threshold = 0.70

    def evaluate_fragments(self, fragments: list[dict[str, Any]]) -> SufficiencyDecision:
        if len(fragments) < self.min_fragments:
            return SufficiencyDecision(
                allowed=False, reason_code="INSUFFICIENT_TIER1_EVIDENCE"
            )

        if any(f.get("tier") != 1 for f in fragments):
            return SufficiencyDecision(
                allowed=False, reason_code="NON_TIER1_FRAGMENT_PRESENT"
            )

        if any(not f.get("citation_label") for f in fragments):
            return SufficiencyDecision(
                allowed=False, reason_code="MISSING_PARAGRAPH_CITATION"
            )

        low_conf = [
            f for f in fragments
            if f.get("confidence", 0) < self.min_confidence_threshold
        ]
        if fragments and len(low_conf) / len(fragments) > self.max_low_confidence_share:
            return SufficiencyDecision(
                allowed=False, reason_code="LOW_CONFIDENCE_EVIDENCE"
            )

        return SufficiencyDecision(allowed=True)

    def evaluate_draft(
        self,
        draft_summary: str | None,
        citations: list[str],
    ) -> SufficiencyDecision:
        if not citations:
            return SufficiencyDecision(
                allowed=False, reason_code="ANSWER_MISSING_CITATIONS"
            )
        if not draft_summary or len(draft_summary) < 20:
            return SufficiencyDecision(
                allowed=False, reason_code="ANSWER_TOO_SHORT"
            )
        return SufficiencyDecision(allowed=True)
