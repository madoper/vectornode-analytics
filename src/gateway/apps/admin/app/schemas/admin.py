__anchor__ = "admin"

from pydantic import BaseModel


class BlockRequest(BaseModel):
    target_id: str
    reason: str
    created_by: str = "admin"


class BlockResponse(BaseModel):
    override_id: str
    target_id: str
    override_type: str
    reason: str
    created_at: str
    anchor: str = "admin"


class UnblockResponse(BaseModel):
    message: str
    anchor: str = "admin"


class BlockEntry(BaseModel):
    override_id: str
    target_id: str
    override_type: str
    reason: str
    created_by: str
    created_at: str


class BlockListResponse(BaseModel):
    entries: list[BlockEntry]
    total: int
    anchor: str = "admin"
