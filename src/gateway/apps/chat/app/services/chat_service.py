__anchor__ = "chat-service"

import uuid
from datetime import UTC, datetime
from typing import Any


class ChatService:
    """In-memory chat session management. Will migrate to PG later."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._messages: dict[str, list[dict[str, Any]]] = {}
        self._feedback: dict[str, dict[str, Any]] = {}

    async def create_session(self, tenant_id: str, title: str | None = None) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        session = {
            "id": session_id,
            "title": title or f"Сессия {now[:10]}",
            "tenant_id": tenant_id,
            "created_at": now,
            "updated_at": now,
        }
        self._sessions[session_id] = session
        self._messages[session_id] = []
        return session

    async def list_sessions(self, tenant_id: str = "web") -> list[dict[str, Any]]:
        sessions = [s for s in self._sessions.values() if s.get("tenant_id") == tenant_id]
        for s in sessions:
            s["message_count"] = len(self._messages.get(s["id"], []))
        return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        return self._messages.get(session_id, [])

    async def add_message(
        self, session_id: str, role: str, content: str,
        citations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if session_id not in self._sessions:
            return {}
        msg_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        msg = {
            "id": msg_id,
            "role": role,
            "content": content,
            "created_at": now,
            "citations": citations or [],
        }
        self._messages.setdefault(session_id, []).append(msg)
        self._sessions[session_id]["updated_at"] = now
        return msg

    async def save_feedback(
        self, session_id: str, message_id: str, rating: int, comment: str | None = None
    ) -> dict[str, Any]:
        fb_id = str(uuid.uuid4())
        self._feedback[fb_id] = {
            "id": fb_id,
            "session_id": session_id,
            "message_id": message_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(UTC).isoformat(),
        }
        return {"id": fb_id, "status": "ok"}
