__anchor__ = "retrieval"
# schema-ref: project-schema.yaml#/services/8

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    subject_type: str | None = None
    regulator: str | None = None
    top_k: int = 10
    min_confidence: float = 0.0


class FragmentResult(BaseModel):
    fragment_id: str
    document_title: str | None = None
    fragment_text: str
    citation_label: str
    score: float = 0.0
    tier: int = 1
    confidence: float = 1.0
    source_domain: str | None = None
    anchor: str = "retrieval"


class SearchResponse(BaseModel):
    query: str
    results: list[FragmentResult]
    total_count: int
    anchor: str = "retrieval"


class FragmentInput(BaseModel):
    fragment_id: str
    document_title: str | None = None
    fragment_text: str
    citation_label: str
    tier: int = 1
    source_domain: str | None = None


class IndexFragmentsRequest(BaseModel):
    fragments: list[FragmentInput]


class IndexFragmentsResponse(BaseModel):
    indexed_count: int
    anchor: str = "retrieval"
