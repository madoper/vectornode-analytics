__anchor__ = "llm-provider-gigachat"

import json
import time
import uuid

import httpx

from backend.shared.llm.clients.base import BaseLlmClient
from backend.shared.llm.contracts import LlmRequest, LlmResponse
from backend.shared.settings import settings

GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1"


class GigaChatClient(BaseLlmClient):
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_id = client_id or settings.gigachat_client_id
        self._client_secret = client_secret or settings.gigachat_secret
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._client = http_client or httpx.AsyncClient(timeout=60.0, verify=False)

    async def _ensure_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 300:
            return self._token
        resp = await self._client.post(
            GIGACHAT_OAUTH_URL,
            auth=(self._client_id, self._client_secret),
            data={"scope": "GIGACHAT_API_PERS"},
            headers={
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 1800)
        return self._token

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        token = await self._ensure_token()

        system_msg = {
            "role": "system",
            "content": (
                "Ты — эксперт ФНС по анализу финансовых рисков. "
                "На основе представленных фрагментов нормативных документов "
                "и судебной практики ответь на вопрос пользователя. "
                "Ссылайся на конкретные статьи и пункты НПА. "
                "Если информации недостаточно — честно скажи об этом. "
                "Отвечай строго на русском языке."
            ),
        }
        messages = [system_msg, {"role": "user", "content": request.prompt}]
        payload = {
            "model": "GigaChat:latest",
            "messages": messages,
            "temperature": 0.3,
        }

        resp = await self._client.post(
            f"{GIGACHAT_API_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            content=json.dumps(payload),
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        content = choice["message"].get("content") or ""
        usage = data.get("usage", {})

        return LlmResponse(
            content=content,
            model_used=data.get("model", "GigaChat:latest"),
            tokens_input=usage.get("prompt_tokens", 0),
            tokens_output=usage.get("completion_tokens", 0),
        )
