__anchor__ = "llm-provider-router"

import json

import httpx

from backend.shared.llm.clients.base import BaseLlmClient
from backend.shared.llm.contracts import LlmRequest, LlmResponse
from backend.shared.settings import settings


class OpenAiClient(BaseLlmClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key or settings.llm_api_key
        self._model = model or settings.llm_model
        self._base_url = base_url
        self._client = http_client or httpx.AsyncClient(timeout=60.0)

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        if not self._api_key:
            msg = "OpenAI API key not configured"
            raise RuntimeError(msg)

        messages = [{"role": "user", "content": request.prompt}]
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


class YandexGptClient(BaseLlmClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "yandexgpt-lite",
        catalog_id: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key or settings.llm_api_key
        self._model = model
        self._catalog_id = catalog_id or ""
        self._client = http_client or httpx.AsyncClient(timeout=60.0)

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        if not self._api_key:
            msg = "YandexGPT API key not configured"
            raise RuntimeError(msg)

        payload = {
            "modelUri": f"gpt://{self._catalog_id}/{self._model}",
            "completionOptions": {
                "stream": False,
                "temperature": request.temperature,
            },
            "messages": [
                {"role": "system", "text": "Ты — ассистент по ПОД/ФТ/ФРОМУ. Отвечай строго на русском языке."},  # noqa: E501
                {"role": "user", "text": request.prompt},
            ],
        }

        response = await self._client.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "x-folder-id": self._catalog_id,
            },
            content=json.dumps(payload),
        )
        response.raise_for_status()
        data = response.json()

        message = data["result"]["alternatives"][0]["message"]
        usage = data["result"].get("usage", {})

        return LlmResponse(
            content=message.get("text", ""),
            model_used=self._model,
            tokens_input=usage.get("inputTextTokens", 0),
            tokens_output=usage.get("outputTextTokens", 0),
        )
