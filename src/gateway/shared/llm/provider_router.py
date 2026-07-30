__anchor__ = "llm-provider-router"

from typing import Protocol

from backend.shared.llm.clients.base import BaseLlmClient
from backend.shared.llm.clients.openai import OpenAiClient, YandexGptClient
from backend.shared.llm.clients.openrouter import OpenRouterClient
from backend.shared.llm.clients.gigachat import GigaChatClient
from backend.shared.llm.contracts import LlmRequest, LlmResponse
from backend.shared.llm.prompts.drafting import build_drafting_prompt
from backend.shared.llm.prompts.extraction import build_extraction_prompt
from backend.shared.llm.prompts.verification import build_verification_prompt
from backend.shared.settings import settings


class _PolicyEngine(Protocol):
    def select(self, task_type: str) -> list[str]: ...


_drafting_prompt = build_drafting_prompt
_extraction_prompt = build_extraction_prompt
_verification_prompt = build_verification_prompt


class LlmProviderRouter:
    """All LLM calls go through this module. No direct calls from feature code."""

    def __init__(
        self, providers: dict[str, BaseLlmClient], policy_engine: _PolicyEngine | None = None
    ) -> None:
        self._providers = providers
        self._policy_engine = policy_engine

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        candidates = (
            self._policy_engine.select(task_type=request.task_type)
            if self._policy_engine
            else list(self._providers)
        )
        last_error: Exception | None = None
        for provider_name in candidates:
            client = self._providers[provider_name]
            try:
                return await client.invoke(request)
            except Exception as exc:
                last_error = exc
                continue
        msg = f"All providers failed for task={request.task_type}: {last_error}"
        raise RuntimeError(msg)


class MockProvider(BaseLlmClient):
    """Fallback when no LLM API key is configured. Returns canned responses."""

    async def invoke(self, request: LlmRequest) -> LlmResponse:
        task = request.task_type
        if task == "drafting":
            return LlmResponse(
                content='{"summary": "Демо-ответ", "citations_used": [], "gaps": []}',
                model_used="mock",
            )
        if task == "verification":
            return LlmResponse(
                content='{"is_supported": true, "unsupported_claims": [], "missing_citations": [], "confidence": 1.0, "explanation": "Mock verifier"}',  # noqa: E501
                model_used="mock",
            )
        if task == "extraction":
            return LlmResponse(
                content='{"norms": [], "obligations": []}',
                model_used="mock",
            )
        return LlmResponse(content="{}", model_used="mock")


def create_llm_router() -> LlmProviderRouter:
    """Factory: creates a configured LlmProviderRouter based on settings."""
    providers: dict[str, BaseLlmClient] = {}

    if settings.llm_api_key:
        if settings.llm_provider == "openai":
            providers["openai"] = OpenAiClient()
        elif settings.llm_provider == "yandexgpt":
            providers["yandexgpt"] = YandexGptClient()
        elif settings.llm_provider == "openrouter":
            providers["openrouter"] = OpenRouterClient()
        elif settings.llm_provider == "gigachat":
            providers["gigachat"] = GigaChatClient()

    if not providers:
        providers["mock"] = MockProvider()

    return LlmProviderRouter(providers)


def create_summarization_router() -> LlmProviderRouter | None:
    """Factory for summarization-specific LLM router. Returns None if no credentials."""
    prov: dict[str, BaseLlmClient] = {}
    if settings.llm_summarization_provider == "gigachat":
        if settings.gigachat_client_id and settings.gigachat_secret:
            prov["summarization"] = GigaChatClient()
    elif settings.llm_summarization_provider == "openrouter":
        if settings.llm_api_key:
            prov["summarization"] = OpenRouterClient(
                model=settings.llm_summarization_model
            )
    elif settings.llm_summarization_provider == "openai":
        if settings.llm_api_key:
            prov["summarization"] = OpenAiClient()
    else:
        if settings.llm_api_key:
            prov["summarization"] = OpenRouterClient(
                model=settings.llm_summarization_model
            )
    if not prov:
        return None
    return LlmProviderRouter(prov)
