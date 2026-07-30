__anchor__ = "chat-service"

from typing import Any

from pydantic import BaseModel


class ChatSessionCreate(BaseModel):
    title: str | None = None
    tenant_id: str = "web"


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0




class ChatMessageResponse(BaseModel):
    id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: str
    citations: list[dict[str, Any]] | None = None


class FeedbackCreate(BaseModel):
    session_id: str
    message_id: str
    rating: int  # 1 or -1
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    status: str
