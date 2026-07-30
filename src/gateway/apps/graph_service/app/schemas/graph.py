__anchor__ = "graph-service"
# schema-ref: project-schema.yaml#/services/7

from typing import Any

from pydantic import BaseModel


class SyncDocumentRequest(BaseModel):
    document_id: str
    document_version_id: str
    regulator_code: str | None = None
    fragments: list[dict[str, Any]] = []
    obligations: list[dict[str, Any]] = []
    norms: list[dict[str, Any]] = []


class SyncDocumentResponse(BaseModel):
    document_id: str
    nodes_created: int
    edges_created: int
    anchor: str = "graph-service"


class GraphQueryRequest(BaseModel):
    query: str


class GraphNodeResponse(BaseModel):
    id: str
    label: str
    properties: dict[str, Any]
    anchor: str = "graph-service"


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    properties: dict[str, Any] = {}
    anchor: str = "graph-service"


class GraphQueryResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
    node_count: int
    edge_count: int
    anchor: str = "graph-service"
