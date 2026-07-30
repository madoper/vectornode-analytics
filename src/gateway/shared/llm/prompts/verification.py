__anchor__ = "llm-provider-router"

from typing import Any

VERIFICATION_PROMPT = """Ты — верификатор ответов по ПОД/ФТ/ФРОМУ.

Вопрос пользователя: {question}

Черновик ответа: {draft_answer}

Фрагменты-доказательства:
{evidence}

Проверь:
1. Каждый ли факт в ответе подтверждается хотя бы одним фрагментом?
2. Все ли фрагменты относятся к Tier-1 официальным источникам?
3. Нет ли в ответе утверждений, не основанных на предоставленных фрагментах?

Ответь в формате JSON:
{{
  "is_supported": true/false,
  "unsupported_claims": ["..."],
  "missing_citations": ["..."],
  "confidence": 0.0-1.0,
  "explanation": "..."
}}
"""


def build_verification_prompt(
    question: str, draft_answer: str, evidence: list[dict[str, Any]]
) -> str:
    evidence_text = "\n".join(
        f"- [{e.get('citation_label', '?')}] {e.get('fragment_text', e.get('quote', ''))[:500]}"
        for e in evidence
    )
    return VERIFICATION_PROMPT.format(
        question=question,
        draft_answer=draft_answer,
        evidence=evidence_text,
    )
