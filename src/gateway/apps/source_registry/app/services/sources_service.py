__anchor__ = "source-registry"

from typing import Any

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


class SourcesService:
    async def list_sources(self) -> list[dict[str, Any]]:
        return list(_sources)
