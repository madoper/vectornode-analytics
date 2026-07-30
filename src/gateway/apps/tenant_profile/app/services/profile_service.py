__anchor__ = "tenant-profile"

import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.tenant_profile.app.schemas.profile import (
    ApplicabilityResponse,
    ApplicabilityRuleDto,
    DeleteResponse,
    ProfileListResponse,
    ProfileResponse,
    SubjectProfileDto,
)


class ProfileService:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}

    async def create_profile(
        self,
        tenant_id: str,
        subject_type: str,
        regulator: str | None = None,
        extra_criteria: dict[str, Any] | None = None,
    ) -> ProfileResponse:
        profile_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        entry = {
            "id": profile_id,
            "tenant_id": tenant_id,
            "subject_type": subject_type,
            "regulator": regulator,
            "extra_criteria": extra_criteria or {},
            "created_at": now,
        }
        self._profiles[profile_id] = entry
        return ProfileResponse(
            id=profile_id,
            tenant_id=tenant_id,
            subject_type=subject_type,
            regulator=regulator,
            extra_criteria=extra_criteria or {},
            created_at=now,
        )

    async def get_profile(self, profile_id: str) -> ProfileResponse | None:
        entry = self._profiles.get(profile_id)
        if entry is None:
            return None
        return ProfileResponse(**entry)

    async def get_profiles_by_tenant(self, tenant_id: str) -> ProfileListResponse:
        entries = [
            ProfileResponse(**p)
            for p in self._profiles.values()
            if p["tenant_id"] == tenant_id
        ]
        return ProfileListResponse(profiles=entries, total=len(entries))

    async def update_profile(
        self,
        profile_id: str,
        subject_type: str | None = None,
        regulator: str | None = None,
        extra_criteria: dict[str, Any] | None = None,
    ) -> ProfileResponse | None:
        entry = self._profiles.get(profile_id)
        if entry is None:
            return None
        if subject_type is not None:
            entry["subject_type"] = subject_type
        if regulator is not None:
            entry["regulator"] = regulator
        if extra_criteria is not None:
            entry["extra_criteria"] = extra_criteria
        return ProfileResponse(**entry)

    async def delete_profile(self, profile_id: str) -> DeleteResponse:
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            return DeleteResponse(message=f"Profile {profile_id} deleted")
        return DeleteResponse(message=f"Profile {profile_id} not found")

    async def evaluate_applicability(
        self, tenant_id: str, profile: SubjectProfileDto
    ) -> ApplicabilityResponse:
        rules = _get_applicability_rules(profile)
        return ApplicabilityResponse(
            tenant_id=tenant_id,
            profile=profile,
            rules=rules,
        )


def _get_applicability_rules(profile: SubjectProfileDto) -> list[ApplicabilityRuleDto]:
    result: list[ApplicabilityRuleDto] = []

    article_7_1_rules: dict[str, tuple[str, str, bool]] = {
        "OBL-001": ("7.1-ФЗ общие требования", "Разработать ПВК", True),
        "OBL-002": ("7.1-ФЗ общие требования", "Назначить ответственное лицо", True),
        "OBL-003": ("7.1-ФЗ общие требования", "Обучать сотрудников ПОД/ФТ", True),
    }

    credit_rules: dict[str, tuple[str, str, bool]] = {
        "OBL-004": ("Банк России требование", "Уведомлять о подозрительных операциях в ЦБ", True),
        "OBL-005": ("Банк России требование", "Внедрить АС ПОД/ФТ", True),
        "OBL-006": ("Банк России требование", "Направлять ОПС в уполномоченный орган", True),
    }

    if profile.subject_type == "article_7_1":
        for code, (norm, obligation, applies) in article_7_1_rules.items():
            result.append(ApplicabilityRuleDto(
                norm_code=code,
                norm_title=norm,
                obligation_code=obligation,
                applies=applies,
                reason="Применимо для субъектов статьи 7.1",
            ))

    reg = (profile.regulator or "").lower()
    if "банк" in reg or "cbr" in reg:
        for code, (norm, obligation, applies) in credit_rules.items():
            result.append(ApplicabilityRuleDto(
                norm_code=code,
                norm_title=norm,
                obligation_code=obligation,
                applies=applies,
                reason="Применимо для поднадзорных Банку России",
            ))

    if not result:
        result.append(ApplicabilityRuleDto(
            norm_code="GENERAL",
            norm_title="Общие требования ПОД/ФТ",
            obligation_code="Соблюдать требования 115-ФЗ",
            applies=True,
            reason="Базовые требования применимы ко всем субъектам",
        ))

    return result
