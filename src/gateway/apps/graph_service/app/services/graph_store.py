__anchor__ = "graph-service"
# schema-ref: project-schema.yaml#/services/7

import uuid
from typing import Any

from backend.shared.db.neo4j import Neo4jClient
from backend.shared.logging import logger


class GraphStore:
    """Graph store backed by Neo4j with in-memory fallback."""

    def __init__(self, neo4j: Neo4jClient | None = None) -> None:
        self._neo4j = neo4j
        self._in_memory = InMemoryGraphStore()

    @property
    def _use_neo4j(self) -> bool:
        return self._neo4j is not None and self._neo4j.available

    async def sync_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._use_neo4j:
            return await self._sync_neo4j(payload)
        return await self._in_memory.sync_document(payload)

    async def query(self, query: str) -> dict[str, Any]:
        if self._use_neo4j:
            return await self._query_neo4j(query)
        return await self._in_memory.query(query)

    async def get_nodes_by_label(self, label: str) -> list[dict[str, Any]]:
        if self._use_neo4j:
            assert self._neo4j is not None
            result = await self._neo4j.run("MATCH (n:$label) RETURN n", {"label": label})
            return [r["n"] for r in result]
        return await self._in_memory.get_nodes_by_label(label)

    # ── Neo4j operations ──────────────────────────────────────────────

    async def _sync_neo4j(self, payload: dict[str, Any]) -> dict[str, Any]:
        assert self._neo4j is not None
        doc_id = payload["document_id"]
        nodes_created = 0
        edges_created = 0

        await self._neo4j.run(
            "MERGE (d:Document {id: $id}) SET d.version_id = $version_id",
            {"id": doc_id, "version_id": payload["document_version_id"]},
        )
        nodes_created += 1

        reg_code = payload.get("regulator_code", "unknown")
        reg_id = f"reg_{reg_code}"
        await self._neo4j.run(
            "MERGE (r:Regulator {id: $id}) SET r.code = $code",
            {"id": reg_id, "code": reg_code},
        )
        nodes_created += 1
        await self._neo4j.run(
            "MATCH (d:Document {id: $did}), (r:Regulator {id: $rid}) "
            "MERGE (d)-[:PUBLISHED_BY]->(r)",
            {"did": doc_id, "rid": reg_id},
        )
        edges_created += 1

        for f in payload.get("fragments", []):
            fid = f.get("fragment_id", str(uuid.uuid4()))
            await self._neo4j.run(
                "MERGE (f:Fragment {id: $id}) SET f.text = $text",
                {"id": fid, "text": f.get("fragment_text", "")[:80]},
            )
            nodes_created += 1
            await self._neo4j.run(
                "MATCH (f:Fragment {id: $fid}), (d:Document {id: $did}) "
                "MERGE (f)-[:PART_OF_DOCUMENT]->(d)",
                {"fid": fid, "did": doc_id},
            )
            edges_created += 1

        for n in payload.get("norms", []):
            nid = n.get("norm_id", str(uuid.uuid4()))
            await self._neo4j.run(
                "MERGE (n:Norm {id: $id}) SET n.title = $title",
                {"id": nid, "title": n.get("title", "")},
            )
            nodes_created += 1

        for o in payload.get("obligations", []):
            oid = o.get("obligation_id", str(uuid.uuid4()))
            await self._neo4j.run(
                "MERGE (ob:Obligation {id: $id}) SET ob.risk_level = $risk",
                {"id": oid, "risk": o.get("risk_level", "low")},
            )
            nodes_created += 1
            norm_id = o.get("norm_id")
            if norm_id:
                await self._neo4j.run(
                    "MATCH (ob:Obligation {id: $oid}), (n:Norm {id: $nid}) "
                    "MERGE (ob)-[:IMPOSES]->(n)",
                    {"oid": oid, "nid": norm_id},
                )
                edges_created += 1
            for src_id in o.get("source_fragment_ids", []):
                await self._neo4j.run(
                    "MATCH (ob:Obligation {id: $oid}), (f:Fragment {id: $fid}) "
                    "MERGE (ob)-[:SUPPORTED_BY]->(f)",
                    {"oid": oid, "fid": src_id},
                )
                edges_created += 1

        return {
            "document_id": doc_id,
            "nodes_created": nodes_created,
            "edges_created": edges_created,
        }

    async def _query_neo4j(self, query: str) -> dict[str, Any]:
        assert self._neo4j is not None
        try:
            result = await self._neo4j.run(query)
        except Exception as exc:
            logger.error("neo4j query failed", query=query, error=str(exc), anchor="graph-service")
            return {"nodes": [], "edges": []}

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for row in result:
            for val in row.values():
                if isinstance(val, dict) and "id" in val:
                    nid = str(val["id"])
                    if nid not in seen_ids:
                        seen_ids.add(nid)
                        labels = val.get("labels", [None])
                        label = labels[0] if isinstance(labels, list) else str(type(val).__name__)
                        nodes.append({"id": nid, "label": label, "properties": val})
                elif hasattr(val, "items"):
                    for v in val.values():
                        if isinstance(v, dict) and "id" in v:
                            nid = str(v["id"])
                            if nid not in seen_ids:
                                seen_ids.add(nid)
                                nodes.append({
                                    "id": nid,
                                    "label": str(type(v).__name__),
                                    "properties": v,
                                })

        return {"nodes": nodes, "edges": edges}


class InMemoryGraphStore:
    """Pure in-memory fallback."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[dict[str, Any]] = []

    async def sync_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        nodes_created = 0
        edges_created = 0
        doc_id = payload["document_id"]

        self._add_node(doc_id, "Document", {
            "id": doc_id, "version_id": payload["document_version_id"],
        })
        nodes_created += 1

        reg_code = payload.get("regulator_code", "unknown")
        reg_id = f"reg_{reg_code}"
        self._add_node(reg_id, "Regulator", {"id": reg_id, "code": reg_code})
        nodes_created += 1
        self._add_edge(f"e_{doc_id}_reg", doc_id, reg_id, "PUBLISHED_BY")
        edges_created += 1

        for f in payload.get("fragments", []):
            frag_id = f.get("fragment_id", str(uuid.uuid4()))
            self._add_node(frag_id, "Fragment", {
                "id": frag_id, "text": f.get("fragment_text", "")[:80],
            })
            nodes_created += 1
            self._add_edge(f"e_{frag_id}_doc", frag_id, doc_id, "PART_OF_DOCUMENT")
            edges_created += 1

        for n in payload.get("norms", []):
            norm_id = n.get("norm_id", str(uuid.uuid4()))
            self._add_node(norm_id, "Norm", {"id": norm_id, "title": n.get("title", "")})
            nodes_created += 1

        for o in payload.get("obligations", []):
            ob_id = o.get("obligation_id", str(uuid.uuid4()))
            self._add_node(ob_id, "Obligation", {
                "id": ob_id, "risk_level": o.get("risk_level", "low"),
            })
            nodes_created += 1
            norm_id = o.get("norm_id")
            if norm_id:
                self._add_edge(f"e_{ob_id}_norm", ob_id, norm_id, "IMPOSES")
                edges_created += 1
            for src_id in o.get("source_fragment_ids", []):
                self._add_edge(f"e_{ob_id}_{src_id}", ob_id, src_id, "SUPPORTED_BY")
                edges_created += 1

        return {
            "document_id": doc_id,
            "nodes_created": nodes_created,
            "edges_created": edges_created,
        }

    async def query(self, query: str) -> dict[str, Any]:
        import re
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        labels_found = []
        for label in ["Regulator", "Document", "Fragment", "Norm", "Obligation", "SubjectType"]:
            if f":{label}" in query:
                labels_found.append(label)
        id_match = re.search(r"\{\s*id:\s*'([^']+)'\s*\}", query)
        target_id = id_match.group(1) if id_match else None

        for node in self._nodes.values():
            if target_id and node["properties"].get("id") != target_id:
                continue
            if labels_found and node["label"] not in labels_found:
                continue
            nodes.append(node)

        matched_ids = {n["id"] for n in nodes}
        for edge in self._edges:
            source_ok = edge["source"] in matched_ids
            target_ok = edge["target"] in matched_ids
            if source_ok and (target_ok or not target_id):
                edges.append(edge)

        return {"nodes": nodes, "edges": edges}

    async def get_nodes_by_label(self, label: str) -> list[dict[str, Any]]:
        return [n for n in self._nodes.values() if n["label"] == label]

    def _add_node(self, node_id: str, label: str, properties: dict[str, Any]) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = {"id": node_id, "label": label, "properties": properties}

    def _add_edge(self, edge_id: str, source: str, target: str, edge_type: str) -> None:
        self._edges.append({
            "id": edge_id, "source": source, "target": target,
            "type": edge_type, "properties": {},
        })
