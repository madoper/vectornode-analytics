__anchor__ = "admin"

import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.admin.app.schemas.admin import (
    BlockEntry,
    BlockListResponse,
    BlockResponse,
    UnblockResponse,
)


class AdminService:
    def __init__(self) -> None:
        self._overrides: dict[str, dict[str, Any]] = {}
        self._blocked_documents: set[str] = set()
        self._blocked_norms: set[str] = set()

    async def _block(
        self, target_id: str, reason: str, override_type: str, created_by: str
    ) -> BlockResponse:
        override_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        entry = {
            "override_id": override_id,
            "target_id": target_id,
            "override_type": override_type,
            "reason": reason,
            "created_by": created_by,
            "created_at": now,
        }
        self._overrides[override_id] = entry
        if override_type == "block_document":
            self._blocked_documents.add(target_id)
        else:
            self._blocked_norms.add(target_id)
        return BlockResponse(
            override_id=override_id,
            target_id=target_id,
            override_type=override_type,
            reason=reason,
            created_at=now,
        )

    async def block_document(
        self, target_id: str, reason: str, created_by: str = "admin"
    ) -> BlockResponse:
        return await self._block(target_id, reason, "block_document", created_by)

    async def block_norm(
        self, target_id: str, reason: str, created_by: str = "admin"
    ) -> BlockResponse:
        return await self._block(target_id, reason, "block_norm", created_by)

    async def unblock(self, target_id: str) -> UnblockResponse:
        removed_doc = target_id in self._blocked_documents
        removed_norm = target_id in self._blocked_norms
        self._blocked_documents.discard(target_id)
        self._blocked_norms.discard(target_id)

        to_delete = [
            oid for oid, entry in self._overrides.items()
            if entry["target_id"] == target_id
        ]
        for oid in to_delete:
            del self._overrides[oid]

        if removed_doc or removed_norm:
            return UnblockResponse(
                message=f"Target {target_id} unblocked successfully",
            )
        return UnblockResponse(
            message=f"Target {target_id} was not blocked",
        )

    async def list_blocks(self) -> BlockListResponse:
        entries = [
            BlockEntry(
                override_id=e["override_id"],
                target_id=e["target_id"],
                override_type=e["override_type"],
                reason=e["reason"],
                created_by=e["created_by"],
                created_at=e["created_at"],
            )
            for e in sorted(
                self._overrides.values(), key=lambda x: x["created_at"], reverse=True
            )
        ]
        return BlockListResponse(entries=entries, total=len(entries))

    def is_document_blocked(self, document_id: str) -> bool:
        return document_id in self._blocked_documents

    def is_norm_blocked(self, norm_id: str) -> bool:
        return norm_id in self._blocked_norms
