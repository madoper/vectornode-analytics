__anchor__ = "llm-provider-router"
# schema-ref: project-schema.yaml#/shared_modules/0

from pydantic import BaseModel


class LlmTaskType:
    EXTRACTION = "extraction"
    RERANK = "rerank"
    DRAFTING = "drafting"
    VERIFICATION = "verification"
    SUMMARIZATION = "summarization"


class LlmRequest(BaseModel):
    task_type: str
    prompt: str
    model: str | None = None
    temperature: float = 0.0


class LlmResponse(BaseModel):
    content: str
    model_used: str
    tokens_input: int = 0
    tokens_output: int = 0
