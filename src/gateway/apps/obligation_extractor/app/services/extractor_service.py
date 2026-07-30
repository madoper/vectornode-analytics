__anchor__ = "obligation-extractor"
# schema-ref: project-schema.yaml#/services/6

import re
import uuid
from typing import Any


class ObligationExtractorService:
    """Extracts norms and obligations from regulatory document fragments.

    In production, this delegates to an LLM via provider_router.
    For Sprint 3, uses pattern matching for a working skeleton.
    """

    def __init__(self) -> None:
        self._norms: dict[str, dict[str, Any]] = {}
        self._obligations: dict[str, dict[str, Any]] = {}

    async def extract(
        self,
        document_id: str,
        document_version_id: str,  # noqa: ARG002
        fragments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        norms: list[dict[str, Any]] = []
        obligations: list[dict[str, Any]] = []

        for frag in fragments:
            norms_found = self._extract_norms(frag)
            for norm in norms_found:
                norm_id = str(uuid.uuid4())
                norm["norm_id"] = norm_id
                self._norms[norm_id] = norm
                norms.append(norm)

                obligations_found = self._extract_obligations(frag, norm_id)
                for ob in obligations_found:
                    ob_id = str(uuid.uuid4())
                    ob["obligation_id"] = ob_id
                    ob["source_fragment_ids"] = [frag["fragment_id"]]
                    self._obligations[ob_id] = ob
                    obligations.append(ob)

        return {
            "document_id": document_id,
            "norms": norms,
            "obligations": obligations,
            "norm_count": len(norms),
            "obligation_count": len(obligations),
        }

    async def list_norms(self) -> list[dict[str, Any]]:
        return list(self._norms.values())

    async def list_obligations(self) -> list[dict[str, Any]]:
        return list(self._obligations.values())

    async def get_obligations_by_norm(self, norm_id: str) -> list[dict[str, Any]]:
        norm = self._norms.get(norm_id)
        if not norm:
            return []
        return [o for o in self._obligations.values() if o["norm_id"] == norm_id]

    def _extract_norms(self, fragment: dict[str, Any]) -> list[dict[str, Any]]:
        text = fragment.get("fragment_text", "")
        norms: list[dict[str, Any]] = []

        # Detect potential norm-bearing fragments by keyword patterns
        keywords = [
            "обязан", "должен", "требуется", "необходимо", "запрещается",
            "разрешается", "предусмотрено", "установлено", "вправе",
        ]
        has_obligation_keywords = any(kw in text.lower() for kw in keywords)
        if not has_obligation_keywords:
            return norms

        norm_type = self._detect_norm_type(text)
        match = re.search(r"стать[яиюе]\s*(\d+[\.\d]*)", text.lower())
        norm_code = f"ст. {match.group(1)}" if match else None

        norms.append({
            "norm_code": norm_code,
            "title": text[:80],
            "norm_type": norm_type,
            "summary": text[:200],
            "confidence_score": 0.75 if norm_code else 0.50,
        })
        return norms

    def _detect_norm_type(self, text: str) -> str:
        if any(kw in text.lower() for kw in ["запрещается", "не допускается"]):
            return "prohibition"
        if any(kw in text.lower() for kw in ["обязан", "должен", "требуется"]):
            return "obligation"
        if any(kw in text.lower() for kw in ["вправе", "разрешается"]):
            return "permission"
        return "requirement"

    def _extract_obligations(
        self, fragment: dict[str, Any], norm_id: str
    ) -> list[dict[str, Any]]:
        text = fragment.get("fragment_text", "")
        obligations: list[dict[str, Any]] = []

        actions = self._extract_actions(text)
        if not actions:
            return obligations

        obligations.append({
            "norm_id": norm_id,
            "obligation_code": None,
            "subject_scope": {"all": True},
            "required_actions": actions,
            "risk_level": self._detect_risk_level(text),
            "confidence_score": 0.60,
            "source_fragment_ids": [],
        })
        return obligations

    def _extract_actions(self, text: str) -> list[str]:
        actions: list[str] = []
        patterns = [
            r"обязан\s+(.+?)(?:\.|;|$)",
            r"должен\s+(.+?)(?:\.|;|$)",
            r"необходимо\s+(.+?)(?:\.|;|$)",
            r"требуется\s+(.+?)(?:\.|;|$)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend(m.strip() for m in matches if m.strip())
        return actions

    def _detect_risk_level(self, text: str) -> str:
        if any(kw in text.lower() for kw in ["повышенн", "особый", "высокий"]):
            return "high"
        if any(kw in text.lower() for kw in ["средн"]):
            return "medium"
        return "low"
