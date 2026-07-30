__anchor__ = "tenant-profile"

from typing import Any

from pydantic import BaseModel, Field


class SubjectProfileDto(BaseModel):
    subject_type: str
    regulator: str | None = None
    extra_criteria: dict[str, Any] = Field(default_factory=dict)


class CreateProfileRequest(BaseModel):
    tenant_id: str
    subject_type: str
    regulator: str | None = None
    extra_criteria: dict[str, Any] = Field(default_factory=dict)


class UpdateProfileRequest(BaseModel):
    subject_type: str | None = None
    regulator: str | None = None
    extra_criteria: dict[str, Any] | None = None


class ProfileResponse(BaseModel):
    id: str
    tenant_id: str
    subject_type: str
    regulator: str | None
    extra_criteria: dict[str, Any]
    created_at: str
    anchor: str = "tenant-profile"


class ProfileListResponse(BaseModel):
    profiles: list[ProfileResponse]
    total: int
    anchor: str = "tenant-profile"


class ApplicabilityRuleDto(BaseModel):
    norm_code: str
    norm_title: str
    obligation_code: str
    applies: bool
    reason: str


class ApplicabilityResponse(BaseModel):
    tenant_id: str
    profile: SubjectProfileDto
    rules: list[ApplicabilityRuleDto]
    anchor: str = "tenant-profile"


class DeleteResponse(BaseModel):
    message: str
    anchor: str = "tenant-profile"
