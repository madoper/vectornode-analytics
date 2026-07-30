__anchor__ = "llm-provider-router"

from typing import Any

DRAFTING_PROMPT = (
    """Ты — ассистент по ПОД/ФТ/ФРОМУ. """
    """Сформируй extractive-ответ, используя ТОЛЬКО предоставленные фрагменты.

Вопрос: {question}

Фрагменты:
{evidence}

Правила:
- Используй ТОЛЬКО информацию из фрагментов.
- Каждое утверждение должно сопровождаться citation_label.
- Если фрагментов недостаточно для полного ответа, укажи это.
- Ответ должен быть на русском языке.

Сформируй ответ в формате:
{{
  "summary": "текст ответа с цитированием",
  "citations_used": ["citation_label_1", "citation_label_2"],
  "gaps": ["вопрос, на который нет ответа в фрагментах"]
}}
"""
)


def build_drafting_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    evidence_text = "\n".join(
        f"[{e.get('citation_label', '?')}] {e.get('fragment_text', e.get('quote', ''))[:500]}"
        for e in evidence
    )
    return DRAFTING_PROMPT.format(question=question, evidence=evidence_text)
