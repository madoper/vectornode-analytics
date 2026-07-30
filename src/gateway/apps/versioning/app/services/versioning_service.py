__anchor__ = "versioning"
# schema-ref: project-schema.yaml#/services/5

import uuid
from datetime import UTC, datetime
from typing import Any


class VersioningService:
    """Manages document registration, version detection, and timeline."""

    def __init__(self) -> None:
        self._documents: dict[str, dict[str, Any]] = {}
        self._versions: dict[str, list[dict[str, Any]]] = {}

    async def register_document(
        self,
        canonical_url: str,
        document_title: str | None,
        document_kind: str,
        content_hash: str,
        regulator_code: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        version_id = str(uuid.uuid4())

        # Find existing document by URL
        found_id: str | None = None
        for _id, doc in self._documents.items():
            if doc["canonical_url"] == canonical_url:
                found_id = _id
                break

        if found_id is None:
            doc_id = str(uuid.uuid4())
            self._documents[doc_id] = {
                "id": doc_id,
                "canonical_url": canonical_url,
                "title": document_title or canonical_url,
                "document_kind": document_kind,
                "regulator_code": regulator_code,
                "status": "active",
                "first_seen_at": now,
                "last_seen_at": now,
            }
            self._versions[doc_id] = []
        else:
            doc_id = found_id
            self._documents[doc_id]["last_seen_at"] = now

        existing_versions = self._versions.get(doc_id, [])
        for v in existing_versions:
            if v["content_hash"] == content_hash:
                # Same content — not a new version
                return {
                    "document_id": doc_id,
                    "version_id": v["id"],
                    "is_new_version": False,
                    "version_label": v.get("version_label"),
                    "is_current": v["is_current"],
                }

        # New version
        version_no = len(existing_versions) + 1
        # Mark previous versions as not current
        for v in existing_versions:
            v["is_current"] = False

        version_entry: dict[str, Any] = {
            "id": version_id,
            "document_id": doc_id,
            "version_label": f"v{version_no}",
            "effective_from": now[:10],
            "effective_to": None,
            "fetched_at": now,
            "content_hash": content_hash,
            "is_current": True,
        }
        self._versions[doc_id].append(version_entry)

        return {
            "document_id": doc_id,
            "version_id": version_id,
            "is_new_version": True,
            "version_label": f"v{version_no}",
            "is_current": True,
        }

    async def list_versions(self, document_id: str) -> list[dict[str, Any]]:
        return self._versions.get(document_id, [])

    async def get_document(self, document_id: str) -> dict[str, Any] | None:
        return self._documents.get(document_id)
