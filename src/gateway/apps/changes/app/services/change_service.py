__anchor__ = "changes"

import hashlib
from datetime import UTC, datetime
from typing import Any

from backend.apps.changes.app.schemas.changes import (
    ChangeItem,
    ChangesListResponse,
    FragmentDiff,
    VersionDiffResponse,
)
from backend.apps.versioning.app.services.versioning_service import VersioningService


class ChangeDetectionService:
    def __init__(self) -> None:
        self._versioning = VersioningService()
        self._change_log: list[dict[str, Any]] = []

    async def record_change(
        self,
        document_id: str,
        title: str,
        version_label: str,
        change_type: str,
    ) -> None:
        self._change_log.append({
            "document_id": document_id,
            "title": title,
            "version_label": version_label,
            "change_type": change_type,
            "effective_from": datetime.now(UTC).isoformat()[:10],
            "summary": f"Document '{title}' {change_type} as version {version_label}",
            "detected_at": datetime.now(UTC).isoformat(),
        })

    async def list_changes(self, limit: int = 50) -> ChangesListResponse:
        sorted_log = sorted(
            self._change_log, key=lambda c: c["detected_at"], reverse=True
        )[:limit]
        items = [
            ChangeItem(
                document_id=e["document_id"],
                title=e["title"],
                version_label=e["version_label"],
                change_type=e["change_type"],
                effective_from=e.get("effective_from"),
                summary=e.get("summary"),
            )
            for e in sorted_log
        ]
        return ChangesListResponse(changes=items, total=len(items))

    async def diff_versions(
        self,
        document_id: str,
        from_version_id: str,
        to_version_id: str,
    ) -> VersionDiffResponse | None:
        doc = await self._versioning.get_document(document_id)
        if not doc:
            return None

        versions = await self._versioning.list_versions(document_id)
        from_v: dict[str, Any] | None = None
        to_v: dict[str, Any] | None = None
        for v in versions:
            if v["id"] == from_version_id:
                from_v = v
            if v["id"] == to_version_id:
                to_v = v

        if not from_v or not to_v:
            return None

        from_frags = self._simulate_fragments(from_v["content_hash"])
        to_frags = self._simulate_fragments(to_v["content_hash"])

        changes = self._compute_diff(from_frags, to_frags)

        return VersionDiffResponse(
            document_id=document_id,
            document_title=doc.get("title", ""),
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            from_version_label=from_v.get("version_label"),
            to_version_label=to_v.get("version_label"),
            fragment_changes=changes,
            total_changes=len(changes),
        )

    @staticmethod
    def _simulate_fragments(content_hash: str) -> list[dict[str, Any]]:
        seed = int(hashlib.md5(content_hash.encode()).hexdigest()[:8], 16)
        count = 5 + (seed % 10)
        return [
            {
                "fragment_no": i + 1,
                "citation_label": f"§{i + 1}",
                "text": f"Fragment {i + 1} from hash {content_hash[:8]}",
            }
            for i in range(count)
        ]

    @staticmethod
    def _compute_diff(
        old_frags: list[dict[str, Any]],
        new_frags: list[dict[str, Any]],
    ) -> list[FragmentDiff]:
        old_map = {f["fragment_no"]: f for f in old_frags}
        new_map = {f["fragment_no"]: f for f in new_frags}
        all_keys = sorted(set(old_map.keys()) | set(new_map.keys()))
        diffs: list[FragmentDiff] = []
        for key in all_keys:
            old_f = old_map.get(key)
            new_f = new_map.get(key)
            if old_f and not new_f:
                diffs.append(FragmentDiff(
                    fragment_no=key,
                    citation_label=old_f["citation_label"],
                    old_text=old_f["text"],
                    new_text=None,
                    status="removed",
                ))
            elif not old_f and new_f:
                diffs.append(FragmentDiff(
                    fragment_no=key,
                    citation_label=new_f["citation_label"],
                    old_text=None,
                    new_text=new_f["text"],
                    status="added",
                ))
            elif old_f and new_f and old_f["text"] != new_f["text"]:
                diffs.append(FragmentDiff(
                    fragment_no=key,
                    citation_label=new_f["citation_label"],
                    old_text=old_f["text"],
                    new_text=new_f["text"],
                    status="modified",
                ))
        return diffs
