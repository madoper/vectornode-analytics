__anchor__ = "vector-indexer"
# schema-ref: project-schema.yaml#/services/8

from pydantic import BaseModel


class FragmentInput(BaseModel):
    fragment_id: str
    fragment_text: str
    document_title: str | None = None
    citation_label: str | None = None
    tier: int = 1
    source_domain: str | None = None


class IndexRequest(BaseModel):
    collection: str | None = None
    fragments: list[FragmentInput]


class IndexResponse(BaseModel):
    indexed_count: int
    collection: str
    anchor: str = "vector-indexer"


class DeleteRequest(BaseModel):
    fragment_ids: list[str]
    collection: str | None = None


class DeleteResponse(BaseModel):
    deleted_count: int
    collection: str
    anchor: str = "vector-indexer"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    collection: str | None = None


class SearchHit(BaseModel):
    fragment_id: str
    score: float
    document_title: str | None = None
    fragment_text: str | None = None
    citation_label: str | None = None
    tier: int = 1
    source_domain: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchHit]
    total_count: int
    anchor: str = "vector-indexer"
