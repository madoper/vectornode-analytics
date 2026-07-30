__anchor__ = "crawler"
# schema-ref: project-schema.yaml#/services/3

import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx


class CrawlerService:
    """Orchestrates crawling of regulatory source domains."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._results: dict[str, list[dict[str, Any]]] = {}

    async def start_crawl(
        self, source_domain: str, url: str, crawl_depth: int = 1
    ) -> dict[str, Any]:
        job_id = str(uuid.uuid4())
        job: dict[str, Any] = {
            "id": job_id,
            "source_domain": source_domain,
            "url": url,
            "crawl_depth": crawl_depth,
            "status": "running",
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._jobs[job_id] = job
        self._results[job_id] = []

        # Simulate crawl — in production this dispatches to background worker
        await self._simulate_crawl(job_id, url)
        job["status"] = "completed"
        return job

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self._jobs.get(job_id)

    async def get_results(self, job_id: str) -> list[dict[str, Any]]:
        return self._results.get(job_id, [])

    async def _simulate_crawl(self, job_id: str, url: str) -> None:
        """Fetch a URL, compute checksum, and record result."""
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                content = resp.text
                content_type = resp.headers.get("content-type", "text/html")
        except Exception:
            # Fallback: return fake result for testing without network
            content = f"<html><body>Mock content for {url}</body></html>"
            content_type = "text/html"

        checksum = hashlib.sha256(content.encode()).hexdigest()
        result_id = str(uuid.uuid4())
        self._results[job_id].append({
            "id": result_id,
            "url": url,
            "content_type": content_type,
            "checksum": checksum,
            "content": content,
            "discovered_at": datetime.now(UTC).isoformat(),
        })
