__anchor__ = "retrieval"
# schema-ref: project-schema.yaml#/services/8

import contextlib
import math
import re
from collections import Counter
from typing import Any


class _SharedState:
    """Borg shared state so all RetrievalService instances share the same BM25 index."""

    _fragments: dict[str, dict[str, Any]] = {}
    _inverted_index: dict[str, dict[str, float]] = {}
    _total_docs: int = 0


class RetrievalService:
    """Hybrid retrieval: BM25-like keyword search + Qdrant vector search.

    BM25 runs on in-memory index for speed. Qdrant vector search runs
    as a parallel strategy; results are merged via reciprocal rank fusion.

    Uses Borg pattern вЂ” all instances share the same BM25 index.
    """

    _shared = _SharedState()

    @classmethod
    def clear_index(cls) -> None:
        cls._shared._fragments.clear()
        cls._shared._inverted_index.clear()
        cls._shared._total_docs = 0

    async def load_from_qdrant(self) -> int:
        try:
            from backend.shared.db.qdrant import QdrantClient
            qdrant = QdrantClient()
            await qdrant.connect()
        except Exception:
            return 0
        try:
            all_points = []
            offset = 0
            batch = await qdrant.scroll_points(limit=100, offset=offset)
            while batch:
                all_points.extend(batch)
                offset += len(batch)
                batch = await qdrant.scroll_points(limit=100, offset=offset)
        except Exception:
            await qdrant.disconnect()
            return 0
        fragments = []
        for p in all_points:
            payload = p["payload"]
            fragments.append({
                "fragment_id": p["fragment_id"],
                "document_title": payload.get("document_title"),
                "fragment_text": payload.get("fragment_text", ""),
                "citation_label": payload.get("citation_label", ""),
                "tier": payload.get("tier", 1),
                "source_domain": payload.get("source_domain"),
            })
        count = await self.index_fragments(fragments)
        with contextlib.suppress(Exception):
            await qdrant.disconnect()
        return count

    def __init__(self, qdrant_client: Any | None = None) -> None:
        self._qdrant = qdrant_client

    async def index_fragments(self, fragments: list[dict[str, Any]]) -> int:
        for f in fragments:
            fid = f["fragment_id"]
            text = f.get("fragment_text", "")
            self._shared._fragments[fid] = f
            tokens = self._tokenize(text)
            tf = Counter(tokens)
            self._shared._inverted_index[fid] = dict(tf)
        self._shared._total_docs = len(self._shared._fragments)
        RetrievalService.save_bm25()
        return len(fragments)

    async def search(
        self,
        query: str,
        subject_type: str | None = None,  # noqa: ARG002
        regulator: str | None = None,
        top_k: int = 10,
        min_confidence: float = 0.0,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        # Strategy 1: BM25 on in-memory index
        bm25_results = await self._search_bm25(query, regulator, top_k)

        # Strategy 2: Qdrant vector search
        qdrant_results = await self._search_qdrant(query, top_k)

        if not bm25_results and not qdrant_results:
            results = self._substring_fallback(query, top_k, regulator)
            self._normalize_scores(results)
            return results

        # Fuse with reciprocal rank fusion
        fused = self._rrf_fuse(bm25_results, qdrant_results, top_k, query=query)
        self._normalize_scores(fused)
        return fused

    async def _search_bm25(
        self, query: str, regulator: str | None, top_k: int
    ) -> list[dict[str, Any]]:
        if not self._shared._fragments:
            return []

        query_tokens = self._tokenize(query)
        scores: list[tuple[str, float]] = []

        for fid, fragment in self._shared._fragments.items():
            score = self._bm25_score(fid, query_tokens)
            if score <= 0:
                continue
            if regulator and fragment.get("source_domain") != regulator:
                continue
            fragment_text = fragment.get("fragment_text", "")
            score += self._phrase_boost(query, fragment_text)
            scores.append((fid, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:top_k]

        results = []
        for fid, score in top:
            frag = self._shared._fragments[fid]
            results.append(self._make_result(frag, score, query=query))
        return results

    async def _search_qdrant(
        self, query: str, top_k: int
    ) -> list[dict[str, Any]]:
        if not self._qdrant:
            return []
        try:
            from backend.apps.vector_indexer.app.services.indexer_service import (
                IndexerService,
            )
            svc = IndexerService(qdrant=self._qdrant)
            return await svc.search(query=query, top_k=top_k)
        except Exception:
            return []

    def _rrf_fuse(
        self,
        bm25: list[dict[str, Any]],
        qdrant: list[dict[str, Any]],
        top_k: int,
        k: int = 60,
        query: str = "",
    ) -> list[dict[str, Any]]:
        """Reciprocal rank fusion of two result lists."""
        scores: dict[str, float] = {}
        store: dict[str, dict[str, Any]] = {}

        for rank, r in enumerate(bm25):
            fid = r["fragment_id"]
            scores[fid] = scores.get(fid, 0) + 1.0 / (k + rank + 1)
            store[fid] = r

        for rank, r in enumerate(qdrant):
            fid = r["fragment_id"]
            scores[fid] = scores.get(fid, 0) + 1.0 / (k + rank + 1)
            if fid not in store:
                store[fid] = self._make_result(
                    self._shared._fragments.get(fid, {}),
                    0,
                    query=query,
                )

        ranked = sorted(store.values(), key=lambda x: scores.get(x["fragment_id"], 0), reverse=True)
        return ranked[:top_k]

    def _make_result(self, frag: dict[str, Any], score: float, query: str = "") -> dict[str, Any]:
        text = frag.get("fragment_text", "")
        if query:
            text = self._highlight_keywords(text, query)
        return {
            "fragment_id": frag["fragment_id"],
            "document_title": frag.get("document_title"),
            "fragment_text": text,
            "citation_label": frag.get("citation_label", ""),
            "score": round(score, 4),
            "confidence_score": 0.0,
            "tier": frag.get("tier", 1),
            "confidence": frag.get("confidence", 0.8),
            "source_domain": frag.get("source_domain"),
        }

    @staticmethod
    def _normalize_scores(results: list[dict[str, Any]]) -> None:
        max_s = max((r["score"] for r in results), default=1.0)
        for r in results:
            r["confidence_score"] = round((r["score"] / max_s) * 100, 1)

    @staticmethod
    def _highlight_keywords(text: str, query: str) -> str:
        tokens = re.findall(r"\w{4,}", query.lower())
        if not tokens:
            return text
        try:
            import pymorphy2
            morph = pymorphy2.MorphAnalyzer()
            query_lemmas: set[str] = set()
            for t in tokens:
                parsed = morph.parse(t)
                if parsed:
                    query_lemmas.add(parsed[0].normal_form.lower())
            if not query_lemmas:
                return text

            def replace_match(m: re.Match[str]) -> str:
                word = m.group()
                parsed = morph.parse(word)
                if parsed and parsed[0].normal_form.lower() in query_lemmas:
                    return f'<mark class="hl">{word}</mark>'
                return str(word)

            return re.sub(r'\b\w+\b', replace_match, text)
        except ImportError:
            pass
        # Fallback: exact match
        for token in sorted(tokens, key=len, reverse=True):
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            text = pattern.sub(lambda m: f'<mark class="hl">{m.group()}</mark>', text)
        return text

    async def list_fragments(self) -> list[dict[str, Any]]:
        return list(self._shared._fragments.values())

    async def remove_fragment(self, fragment_id: str) -> None:
        self._shared._fragments.pop(fragment_id, None)
        self._shared._inverted_index.pop(fragment_id, None)
        self._shared._total_docs = len(self._shared._fragments)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        tokens = re.findall(r"\w{3,}", text)
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "by", "with", "is", "are", "was", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "can", "could", "may", "might", "shall",
            "should", "СЌС‚Рѕ", "РЅРµ", "РєР°Рє", "С‡С‚Рѕ", "РґР»СЏ", "РІ", "РЅР°", "СЃ",
            "РїРѕ", "РѕС‚", "РёР·", "Рє", "Сѓ", "Р·Р°", "Рѕ", "РѕР±", "РїСЂРё",
        }
        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def _bm25_score(self, fid: str, query_tokens: list[str]) -> float:
        k1 = 1.5
        b = 0.75
        doc_tf = self._shared._inverted_index.get(fid, {})
        doc_len = sum(doc_tf.values()) or 1
        avg_doc_len = self._shared._total_docs if self._shared._total_docs > 0 else 1

        score = 0.0
        for token in set(query_tokens):
            tf = doc_tf.get(token, 0)
            if tf == 0:
                continue
            df = sum(1 for d in self._shared._inverted_index.values() if token in d)
            idf = math.log((self._shared._total_docs - df + 0.5) / (df + 0.5) + 1)
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))

        return score

    def _phrase_boost(self, query: str, text: str) -> float:
        """Boost score if whole query phrase appears in fragment text."""
        boost = 0.0
        phrases = re.findall(r'"([^"]+)"', query)
        if not phrases:
            phrases = [query]
        for phrase in phrases:
            if phrase.lower() in text.lower():
                boost += 2.0
        return boost

    def _fallback_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Return mock results when no fragments are indexed."""
        return [
            {
                "fragment_id": "mock-1",
                "document_title": "Mock Document",
                "fragment_text": f"Sample fragment matching query: {query}",
                "citation_label": "С„СЂ. 1",
                "score": 0.85,
                "tier": 1,
                "confidence": 0.85,
                "source_domain": "fedsfm.ru",
            },
            {
                "fragment_id": "mock-2",
                "document_title": "Mock Document",
                "fragment_text": f"Another relevant fragment about: {query}",
                "citation_label": "С„СЂ. 2",
                "score": 0.72,
                "tier": 1,
                "confidence": 0.72,
                "source_domain": "cbr.ru",
            },
        ][:top_k]

    def _substring_fallback(
        self, query: str, top_k: int, regulator: str | None = None
    ) -> list[dict[str, Any]]:
        results = []
        query_tokens = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        for fid, frag in self._shared._fragments.items():
            if regulator and frag.get("source_domain") != regulator:
                continue
            text = frag.get("fragment_text", "").lower()
            frag_tokens = set(re.findall(r"\w+", text))
            score = 0.0
            for qt in query_tokens:
                for ft in frag_tokens:
                    if qt == ft or (len(qt) > 3 and len(ft) > 3 and (qt in ft or ft in qt)):
                        score += 0.5
                        break
            if score > 0:
                text = frag.get("fragment_text", "")
                highlighted = self._highlight_keywords(text, query)
                results.append({
                    "fragment_id": fid,
                    "document_title": frag.get("document_title"),
                    "fragment_text": highlighted,
                    "citation_label": frag.get("citation_label", ""),
                    "score": round(score, 4),
                    "confidence_score": 0.0,
                    "tier": frag.get("tier", 1),
                    "confidence": frag.get("confidence", 0.8),
                    "source_domain": frag.get("source_domain"),
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @classmethod
    def save_bm25(cls, path: str = "/data/bm25_index.pkl") -> bool:
        try:
            import pickle
            state = {
                "_fragments": dict(cls._shared._fragments),
                "_inverted_index": dict(cls._shared._inverted_index),
                "_total_docs": cls._shared._total_docs,
            }
            with open(path, "wb") as f:
                pickle.dump(state, f)
            return True
        except Exception:
            return False

    @classmethod
    def load_bm25(cls, path: str = "/data/bm25_index.pkl") -> bool:
        try:
            import pickle, os
            if not os.path.exists(path):
                return False
            with open(path, "rb") as f:
                state = pickle.load(f)
            cls._shared._fragments = state.get("_fragments", {})
            cls._shared._inverted_index = state.get("_inverted_index", {})
            cls._shared._total_docs = state.get("_total_docs", 0)
            return True
        except Exception:
            return False
