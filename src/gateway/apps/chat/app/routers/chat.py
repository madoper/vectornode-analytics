__anchor__ = "chat-service"

from fastapi import APIRouter, HTTPException

from backend.apps.chat.app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    FeedbackCreate,
    FeedbackResponse,
)
from backend.apps.chat.app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])
_service = ChatService()


@router.post("/chat/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(payload: ChatSessionCreate) -> ChatSessionResponse:
    session = await _service.create_session(tenant_id=payload.tenant_id, title=payload.title)
    return ChatSessionResponse(**session)


@router.get("/chat/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(tenant_id: str = "web") -> list[ChatSessionResponse]:
    sessions = await _service.list_sessions(tenant_id=tenant_id)
    return [ChatSessionResponse(**s) for s in sessions]


@router.get("/chat/sessions/{session_id}", response_model=list[ChatMessageResponse])
async def get_session_messages(session_id: str) -> list[ChatMessageResponse]:
    session = await _service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = await _service.get_messages(session_id)
    return [ChatMessageResponse(**m) for m in messages]


@router.get("/chat/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages_alt(session_id: str) -> list[ChatMessageResponse]:
    session = await _service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = await _service.get_messages(session_id)
    return [ChatMessageResponse(**m) for m in messages]


@router.post("/chat/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackCreate) -> FeedbackResponse:
    result = await _service.save_feedback(
        session_id=payload.session_id,
        message_id=payload.message_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    return FeedbackResponse(**result)
