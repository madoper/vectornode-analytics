__anchor__ = "graph-service"
# schema-ref: project-schema.yaml#/services/7

from fastapi import APIRouter

from backend.apps.graph_service.app.schemas.graph import (
    GraphEdgeResponse,
    GraphNodeResponse,
    GraphQueryRequest,
    GraphQueryResponse,
    SyncDocumentRequest,
    SyncDocumentResponse,
)
from backend.apps.graph_service.app.services.graph_store import GraphStore

router = APIRouter(tags=["graph"])

# When Neo4j unavailable, falls back to in-memory.
_store: GraphStore | None = None


def get_store() -> GraphStore:
    global _store  # noqa: PLW0603
    if _store is None:
        _store = GraphStore()
    return _store


def set_store(store: GraphStore) -> None:
    global _store  # noqa: PLW0603
    _store = store


@router.post("/sync", response_model=SyncDocumentResponse)
async def sync_document(payload: SyncDocumentRequest) -> SyncDocumentResponse:
    result = await get_store().sync_document(payload.model_dump())
    return SyncDocumentResponse(
        document_id=result["document_id"],
        nodes_created=result["nodes_created"],
        edges_created=result["edges_created"],
        anchor="graph-service",
    )


@router.post("/query", response_model=GraphQueryResponse)
async def query_graph(payload: GraphQueryRequest) -> GraphQueryResponse:
    result = await get_store().query(payload.query)
    return GraphQueryResponse(
        nodes=[GraphNodeResponse(**n) for n in result.get("nodes", [])],
        edges=[GraphEdgeResponse(**e) for e in result.get("edges", [])],
        node_count=len(result.get("nodes", [])),
        edge_count=len(result.get("edges", [])),
        anchor="graph-service",
    )


@router.get("/nodes/regulator", response_model=list[GraphNodeResponse])
async def list_regulators() -> list[GraphNodeResponse]:
    nodes = await get_store().get_nodes_by_label("Regulator")
    return [GraphNodeResponse(**n) for n in nodes]


@router.get("/nodes/subject-type", response_model=list[GraphNodeResponse])
async def list_subject_types() -> list[GraphNodeResponse]:
    nodes = await get_store().get_nodes_by_label("SubjectType")
    return [GraphNodeResponse(**n) for n in nodes]


@router.get("/obligations/{obligation_id}/sources", response_model=GraphQueryResponse)
async def get_obligation_sources(obligation_id: str) -> GraphQueryResponse:
    result = await get_store().query(
        f"MATCH (o:Obligation {{id: '{obligation_id}'}})-[:SUPPORTED_BY]->(f:Fragment) RETURN o, f"
    )
    return GraphQueryResponse(
        nodes=[GraphNodeResponse(**n) for n in result.get("nodes", [])],
        edges=[GraphEdgeResponse(**e) for e in result.get("edges", [])],
        node_count=len(result.get("nodes", [])),
        edge_count=len(result.get("edges", [])),
        anchor="graph-service",
    )
