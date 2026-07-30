__anchor__ = "document-upload"

import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.document_upload.app.schemas.upload import UploadResponse
from backend.shared.db.postgres import async_session_factory
from backend.shared.repositories.repos import InternalDocumentRepository
from backend.shared.storage.minio_client import get_minio_client


class UploadService:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._pg_available = True

    async def _try_repo(self) -> InternalDocumentRepository | None:
        if not self._pg_available:
            return None
        try:
            session = async_session_factory()
            return InternalDocumentRepository(session)
        except Exception:
            self._pg_available = False
            return None

    async def upload(
        self,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> UploadResponse:
        import asyncio
        from io import BytesIO

        document_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        safe_name = f"{document_id}_{filename}"
        bucket = "internal-documents"
        try:
            loop = asyncio.get_event_loop()
            minio = get_minio_client()
            buf = BytesIO(content)
            await loop.run_in_executor(
                None,
                lambda: minio.put_object(bucket, safe_name, buf, len(content), content_type),
            )
        except Exception:
            pass

        repo = await self._try_repo()
        if repo is not None:
            try:
                await repo.create(
                    id=uuid.UUID(document_id),
                    title=filename,
                    document_type=content_type or "unknown",
                )
            except Exception:
                self._pg_available = False
                repo = None

        if repo is None:
            self._store[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "content_type": content_type,
                "size_bytes": len(content),
                "created_at": now,
                "storage_path": safe_name,
            }

        return UploadResponse(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
        )

    async def list_documents(self) -> list[UploadResponse]:
        repo = await self._try_repo()
        if repo is not None:
            try:
                models = await repo.list()
                docs = [
                    UploadResponse(
                        document_id=str(m.id),
                        filename=m.title,
                        content_type=m.document_type,
                        size_bytes=0,
                    )
                    for m in models
                ]
                return sorted(docs, key=lambda d: d.document_id, reverse=True)
            except Exception:
                self._pg_available = False

        sorted_docs = sorted(
            self._store.values(), key=lambda d: d["created_at"], reverse=True
        )
        return [
            UploadResponse(
                document_id=d["document_id"],
                filename=d["filename"],
                content_type=d["content_type"],
                size_bytes=d["size_bytes"],
            )
            for d in sorted_docs
        ]
