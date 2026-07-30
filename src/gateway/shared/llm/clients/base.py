__anchor__ = "llm-provider-router"

from abc import ABC, abstractmethod

from backend.shared.llm.contracts import LlmRequest, LlmResponse


class BaseLlmClient(ABC):
    @abstractmethod
    async def invoke(self, request: LlmRequest) -> LlmResponse:
        ...
