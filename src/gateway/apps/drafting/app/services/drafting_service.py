__anchor__ = "drafting"

import uuid
from typing import Any

from backend.apps.drafting.app.schemas.draft import (
    DraftResponse,
    DraftSection,
)
from backend.apps.retrieval.app.services.retrieval_service import RetrievalService
from backend.shared.db.postgres import async_session_factory
from backend.shared.repositories.repos import DraftRepository


class DraftingService:
    DOCUMENT_TEMPLATES: dict[str, dict[str, Any]] = {
        "pvk": {
            "title": "Правила внутреннего контроля",
            "sections": [
                "Общие положения",
                "Программа идентификации",
                "Порядок фиксирования информации",
                "Порядок информирования Росфинмониторинга",
                "Квалификация и обучение сотрудников",
                "Ответственность",
            ],
        },
        "order": {
            "title": "Приказ о назначении ответственного сотрудника",
            "sections": [
                "Назначение",
                "Обязанности",
                "Ответственность",
            ],
        },
        "checklist": {
            "title": "Чек-лист проверки соблюдения требований",
            "sections": [
                "Идентификация клиентов",
                "Фиксирование информации",
                "Порядок направления сообщений",
                "Внутренний контроль",
            ],
        },
    }

    def __init__(self) -> None:
        self._retrieval = RetrievalService()
        self._drafts: dict[str, dict[str, Any]] = {}
        self._pg_available = True

    async def _try_repo(self) -> DraftRepository | None:
        if not self._pg_available:
            return None
        try:
            session = async_session_factory()
            return DraftRepository(session)
        except Exception:
            self._pg_available = False
            return None

    async def generate_draft(  # noqa: PLR0913
        self,
        document_type: str,
        subject_type: str | None = None,  # noqa: ARG002
        context: str | None = None,
        tenant_id: str | None = None,  # noqa: ARG002
    ) -> DraftResponse:
        draft_id = str(uuid.uuid4())
        template = self.DOCUMENT_TEMPLATES.get(document_type)
        if not template:
            template = {
                "title": f"Документ типа {document_type}",
                "sections": ["Общие положения"],
            }

        query = context or template["title"]
        fragments = await self._retrieval.search(query=query, top_k=10)

        sections = []
        for sec_title in template["sections"]:
            sec_fragments = [
                f for f in fragments
                if any(
                    w in (f.get("fragment_text") or "").lower()
                    for w in sec_title.lower().split()[:3]
                )
            ][:3]
            citations = [
                f.get("citation_label", "")
                for f in sec_fragments
                if f.get("citation_label")
            ]
            sample_text = (
                sec_fragments[0].get("fragment_text", "")[:150]
                if sec_fragments
                else "Раздел требует разработки в соответствии с типовой структурой."
            )
            sections.append(DraftSection(
                title=sec_title,
                content=(
                    f"На основе требований:\n{sample_text}"
                    if sec_fragments else "Требуется разработка"
                ),
                citations=citations,
            ))

        matched = sum(1 for s in sections if s.citations)
        summary = (
            f"Сгенерирован проект '{template['title']}'. "
            f"Найдено нормативных ссылок: {len(fragments)}. "
            f"Разделов с обоснованием: {matched}/{len(sections)}."
        )

        result = DraftResponse(
            draft_id=draft_id,
            document_type=document_type,
            title=template["title"],
            sections=sections,
            summary=summary,
        )

        repo = await self._try_repo()
        if repo is not None:
            try:
                await repo.create(
                    id=uuid.UUID(draft_id),
                    title=template["title"],
                    draft_type=document_type,
                    content_json=result.model_dump(),
                    status="draft",
                )
            except Exception:
                self._pg_available = False
                repo = None

        if repo is None:
            self._drafts[draft_id] = result.model_dump()

        return result

    async def get_draft(self, draft_id: str) -> DraftResponse | None:
        repo = await self._try_repo()
        if repo is not None:
            try:
                model = await repo.get(draft_id)
                if model is not None and model.content_json:
                    return DraftResponse(**model.content_json)
            except Exception:
                self._pg_available = False

        data = self._drafts.get(draft_id)
        if data is None:
            return None
        return DraftResponse(**data)

    async def list_drafts(self) -> list[DraftResponse]:
        repo = await self._try_repo()
        if repo is not None:
            try:
                models = await repo.list()
                results = []
                for m in models:
                    if m.content_json:
                        results.append(DraftResponse(**m.content_json))
                return results
            except Exception:
                self._pg_available = False

        return [DraftResponse(**d) for d in self._drafts.values()]
