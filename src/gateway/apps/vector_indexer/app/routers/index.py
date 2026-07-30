__anchor__ = "vector-indexer"
# schema-ref: project-schema.yaml#/services/8

from fastapi import APIRouter

from backend.apps.vector_indexer.app.schemas.indexer import (
    DeleteRequest,
    DeleteResponse,
    IndexRequest,
    IndexResponse,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from backend.apps.vector_indexer.app.services.indexer_service import IndexerService
from backend.shared.db.qdrant import DEFAULT_COLLECTION

router = APIRouter(tags=["vector-indexer"])
_service = IndexerService()


@router.post("/index", response_model=IndexResponse)
async def vector_index_fragments(payload: IndexRequest) -> IndexResponse:
    collection = payload.collection or DEFAULT_COLLECTION
    count = await _service.index_fragments(
        [f.model_dump() for f in payload.fragments],
        collection=collection,
    )
    return IndexResponse(indexed_count=count, collection=collection)


@router.post("/search", response_model=SearchResponse)
async def vector_search_fragments(payload: SearchRequest) -> SearchResponse:
    collection = payload.collection or DEFAULT_COLLECTION
    results = await _service.search(
        query=payload.query,
        top_k=payload.top_k,
        collection=collection,
    )
    return SearchResponse(
        query=payload.query,
        results=[SearchHit(**r) for r in results],
        total_count=len(results),
    )


@router.post("/delete", response_model=DeleteResponse)
async def delete_fragments(payload: DeleteRequest) -> DeleteResponse:
    collection = payload.collection or DEFAULT_COLLECTION
    count = await _service.delete_fragments(
        payload.fragment_ids,
        collection=collection,
    )
    return DeleteResponse(deleted_count=count, collection=collection)
