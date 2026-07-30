__anchor__ = "llm-provider-router"

import json

import httpx

from backend.shared.llm.clients.base import BaseLlmClient
from backend.shared.llm.contracts import LlmRequest, LlmResponse
from backend.shared.settings import settings

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_FREE_MODEL = "poolside/laguna-xs-2.1:free"


class OpenRouterClient(BaseLlmClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = OPENROUTER_BASE_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key or settings.llm_api_key
        self._model = model or settings.llm_model or DEFAULT_FREE_MODEL
        self._base_url = base_url
        self._client = http_client or httpx.AsyncClient(timeout=60.0)

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        if not self._api_key:
            msg = "OpenRouter API key not configured"
            raise RuntimeError(msg)

        system_msg = {
            "role": "system",
            "content": (
                "Ты — ИИ помощник по ПОД/ФТ/ФРОМУ (противодействие "
                "легализации доходов и финансированию терроризма). "
                "Отвечай строго на русском языке. Основывайся на "
                "официальных регуляторных источниках Tier-1."
            ),
        }
        messages = [system_msg, {"role": "user", "content": request.prompt}]
        payload = {
            "model": request.model or self._model,
            "messages": messages,
            "temperature": request.temperature,
        }

        response = await self._client.post(
            f"{self._base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://vectornode.ru",
                "X-Title": "pod-ft",
            },
            content=json.dumps(payload),
        )
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        content = choice["message"]["content"] or ""
        usage = data.get("usage", {})

        return LlmResponse(
            content=content,
            model_used=data.get("model", self._model),
            tokens_input=usage.get("prompt_tokens", 0),
            tokens_output=usage.get("completion_tokens", 0),
        )
