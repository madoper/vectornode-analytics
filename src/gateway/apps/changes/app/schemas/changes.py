__anchor__ = "changes"

from pydantic import BaseModel


class ChangeItem(BaseModel):
    document_id: str
    title: str
    version_label: str
    change_type: str  # "new" | "updated" | "removed"
    effective_from: str | None = None
    summary: str | None = None
    anchor: str = "changes"


class ChangesListResponse(BaseModel):
    changes: list[ChangeItem]
    total: int
    anchor: str = "changes"


class VersionDiffRequest(BaseModel):
    from_version_id: str
    to_version_id: str


class FragmentDiff(BaseModel):
    fragment_no: int
    citation_label: str
    old_text: str | None = None
    new_text: str | None = None
    status: str  # "added" | "removed" | "modified"


class VersionDiffResponse(BaseModel):
    document_id: str
    document_title: str
    from_version_id: str
    to_version_id: str
    from_version_label: str | None = None
    to_version_label: str | None = None
    fragment_changes: list[FragmentDiff]
    total_changes: int
    anchor: str = "changes"
