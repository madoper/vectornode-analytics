__anchor__ = "tenant-profile"

from fastapi import APIRouter, HTTPException, status

from backend.apps.tenant_profile.app.schemas.profile import (
    ApplicabilityResponse,
    CreateProfileRequest,
    DeleteResponse,
    ProfileListResponse,
    ProfileResponse,
    SubjectProfileDto,
    UpdateProfileRequest,
)
from backend.apps.tenant_profile.app.services.profile_service import ProfileService

router = APIRouter(tags=["tenant-profile"])
_service = ProfileService()


@router.post("/tenant-profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(payload: CreateProfileRequest) -> ProfileResponse:
    return await _service.create_profile(
        tenant_id=payload.tenant_id,
        subject_type=payload.subject_type,
        regulator=payload.regulator,
        extra_criteria=payload.extra_criteria,
    )


@router.get("/tenant-profile/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str) -> ProfileResponse:
    result = await _service.get_profile(profile_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return result


@router.get("/tenant-profile/by-tenant/{tenant_id}", response_model=ProfileListResponse)
async def get_profiles_by_tenant(tenant_id: str) -> ProfileListResponse:
    return await _service.get_profiles_by_tenant(tenant_id)


@router.put("/tenant-profile/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, payload: UpdateProfileRequest) -> ProfileResponse:
    result = await _service.update_profile(
        profile_id=profile_id,
        subject_type=payload.subject_type,
        regulator=payload.regulator,
        extra_criteria=payload.extra_criteria,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return result


@router.delete("/tenant-profile/{profile_id}", response_model=DeleteResponse)
async def delete_profile(profile_id: str) -> DeleteResponse:
    return await _service.delete_profile(profile_id)


@router.post("/tenant-profile/{tenant_id}/applicability", response_model=ApplicabilityResponse)
async def evaluate_applicability(  # noqa: E501
    tenant_id: str, profile: SubjectProfileDto
) -> ApplicabilityResponse:
    return await _service.evaluate_applicability(tenant_id, profile)
