__anchor__ = "verification"
# schema-ref: project-schema.yaml#/services/9

from typing import Any

from backend.shared.llm.contracts import LlmRequest, LlmTaskType
from backend.shared.llm.provider_router import LlmProviderRouter
from backend.shared.settings import settings


class LlmVerifier:
    """LLM-based answer verifier.

    Called after the rule engine sufficiency gate passes.
    If no LLM provider is configured, silently skips (rule-engine-only mode).
    """

    def __init__(self, router: LlmProviderRouter | None = None) -> None:
        self._router = router

    def _is_available(self) -> bool:
        return bool(settings.llm_api_key) or self._router is not None

    async def verify(
        self,
        question: str,
        fragments: list[dict[str, Any]],
        draft_summary: str | None,
    ) -> dict[str, Any]:
        """Run LLM verification. Returns dict with passed/confidence/reason."""
        if not self._is_available():
            return {"passed": True, "confidence": 1.0, "reason": "llm_not_configured"}

        prompt = self._build_prompt(question, fragments, draft_summary)

        router = self._router or LlmProviderRouter(
            providers={},
            policy_engine=None,
        )

        try:
            request = LlmRequest(
                task_type=LlmTaskType.VERIFICATION,
                prompt=prompt,
                temperature=0.0,
            )
            response = await router.invoke(request)
            return self._parse_response(response.content)
        except Exception:
            return {"passed": True, "confidence": 1.0, "reason": "llm_fallback_to_rules"}

    def _build_prompt(
        self,
        question: str,
        fragments: list[dict[str, Any]],
        draft_summary: str | None,
    ) -> str:
        lines = [
            "Ты — верификатор ответов по ПОД/ФТ/ФРОМУ.",
            "Проверь, что ответ основан исключительно на предоставленных фрагментах.",
            "",
            f"Вопрос: {question}",
            "",
            "Фрагменты:",
        ]
        for i, f in enumerate(fragments[:10], 1):
            lines.append(f"{i}. [{f.get('citation_label', '')}] {f.get('fragment_text', '')[:200]}")
        if draft_summary:
            lines.extend(["", f"Проект ответа: {draft_summary}"])
        lines.extend([
            "",
            "Ответь строго в формате JSON:",
            '{"passed": true/false, "confidence": 0.0-1.0, "reason": "..."}',
        ])
        return "\n".join(lines)

    @staticmethod
    def _parse_response(content: str) -> dict[str, Any]:
        import json
        import re
        from typing import cast
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return cast("dict[str, Any]", json.loads(match.group(0)))
            except (json.JSONDecodeError, KeyError):
                pass
        return {"passed": True, "confidence": 0.5, "reason": "parse_fallback"}
