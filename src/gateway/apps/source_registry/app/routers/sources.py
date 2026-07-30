__anchor__ = "source-registry"
# schema-ref: project-schema.yaml#/services/2/api/internal

from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.apps.source_registry.app.schemas.sources import (
    CreateSourceRequest,
    SourceDomainResponse,
    UpdateSourceRequest,
)

router = APIRouter(tags=["sources"])

_sources: list[dict[str, Any]] = [
    {"id": "1", "domain": "fedsfm.ru", "source_type": "government",
     "regulator_name": "Росфинмониторинг", "tier": 1, "is_active": True},
    {"id": "2", "domain": "cbr.ru", "source_type": "government",
     "regulator_name": "Банк России", "tier": 1, "is_active": True},
    {"id": "3", "domain": "publication.pravo.gov.ru", "source_type": "government",
     "regulator_name": "Официальное опубликование", "tier": 1, "is_active": True},
    {"id": "4", "domain": "consultant.ru", "source_type": "legal-reference",
     "regulator_name": "КонсультантПлюс", "tier": 2, "is_active": True},
]


@router.get("/sources/active", response_model=list[SourceDomainResponse])
async def list_active_sources() -> list[SourceDomainResponse]:
    active = [s for s in _sources if s["is_active"] and s["tier"] == 1]
    return [SourceDomainResponse(**s) for s in active]


@router.get("/admin/sources", response_model=list[SourceDomainResponse])
async def list_all_sources() -> list[SourceDomainResponse]:
    return [SourceDomainResponse(**s) for s in _sources]


@router.post(
    "/admin/sources", status_code=status.HTTP_201_CREATED, response_model=SourceDomainResponse
)
async def create_source(payload: CreateSourceRequest) -> SourceDomainResponse:
    new_id = str(len(_sources) + 1)
    entry = {"id": new_id, **payload.model_dump()}
    _sources.append(entry)
    return SourceDomainResponse(**entry)


@router.patch("/admin/sources/{source_id}", response_model=SourceDomainResponse)
async def update_source(source_id: str, payload: UpdateSourceRequest) -> SourceDomainResponse:
    for s in _sources:
        if s["id"] == source_id:
            s.update(payload.model_dump(exclude_unset=True))
            return SourceDomainResponse(**s)
    raise HTTPException(status_code=404, detail="Source not found")
