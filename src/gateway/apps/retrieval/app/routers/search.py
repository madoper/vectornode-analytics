__anchor__ = "retrieval"
# schema-ref: project-schema.yaml#/services/8

from typing import Any

from fastapi import APIRouter

from backend.apps.retrieval.app.schemas.search import (
    FragmentResult,
    IndexFragmentsRequest,
    IndexFragmentsResponse,
    SearchRequest,
    SearchResponse,
)
from backend.apps.retrieval.app.services.retrieval_service import RetrievalService

router = APIRouter(tags=["retrieval"])
_service = RetrievalService()

_mock_fallback: list[dict[str, Any]] = [
    {
        "fragment_id": "mock-1",
        "document_title": "Mock Document",
        "fragment_text": "Пример фрагмента, соответствующего запросу.",
        "citation_label": "фр. 1",
        "score": 0.85,
        "tier": 1,
        "confidence": 0.85,
        "source_domain": "fedsfm.ru",
    },
    {
        "fragment_id": "mock-2",
        "document_title": "Mock Document",
        "fragment_text": "Ещё один релевантный фрагмент.",
        "citation_label": "фр. 2",
        "score": 0.72,
        "tier": 1,
        "confidence": 0.72,
        "source_domain": "cbr.ru",
    },
]


@router.post("/search", response_model=SearchResponse)
async def search_fragments(payload: SearchRequest) -> SearchResponse:
    results = await _service.search(
        query=payload.query,
        subject_type=payload.subject_type,
        regulator=payload.regulator,
        top_k=payload.top_k,
        min_confidence=payload.min_confidence,
    )
    if not results:
        results = _mock_fallback[: payload.top_k]
    return SearchResponse(
        query=payload.query,
        results=[FragmentResult(**r) for r in results],
        total_count=len(results),
        anchor="retrieval",
    )


@router.post("/index", response_model=IndexFragmentsResponse)
async def index_fragments(payload: IndexFragmentsRequest) -> IndexFragmentsResponse:
    count = await _service.index_fragments(
        [f.model_dump() for f in payload.fragments]
    )
    return IndexFragmentsResponse(indexed_count=count, anchor="retrieval")


@router.get("/fragments", response_model=list[FragmentResult])
async def list_indexed_fragments() -> list[FragmentResult]:
    fragments = await _service.list_fragments()
    return [FragmentResult(**f) for f in fragments]


@router.delete("/fragments/{fragment_id}", status_code=204)
async def delete_fragment(fragment_id: str) -> None:
    await _service.remove_fragment(fragment_id)
