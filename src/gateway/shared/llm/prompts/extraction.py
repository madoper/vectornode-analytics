__anchor__ = "llm-provider-router"

EXTRACTION_PROMPT = """Извлеки нормы и обязанности из текста официального документа.

Источник: {source_url}
Текст:
{document_text}

Для каждой нормы верни:
{{
  "norms": [
    {{
      "norm_code": "уникальный код нормы",
      "title": "название",
      "norm_type": "requirement|prohibition|recommendation",
      "summary": "краткое содержание"
    }}
  ],
  "obligations": [
    {{
      "obligation_code": "уникальный код",
      "norm_code": "ссылка на норму",
      "subject_scope": ["категории субъектов"],
      "trigger_conditions": ["условия"],
      "required_actions": ["действия"],
      "deadline_rules": ["сроки"]
    }}
  ]
}}

Верни ТОЛЬКО JSON.
"""


def build_extraction_prompt(source_url: str, document_text: str) -> str:
    return EXTRACTION_PROMPT.format(
        source_url=source_url,
        document_text=document_text[:8000],
    )
