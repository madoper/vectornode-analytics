__anchor__ = "workers"
# schema-ref: project-schema.yaml#/services/15

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.workers.app.schemas.job import (
    JobResponse,
    WorkerStatusResponse,
)


class WorkerService:
    """Background job processing service.

    Jobs are executed synchronously on submission for Sprint 4.
    In Sprint 5+ this will use Redis queue and sub-process workers.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._started_at = datetime.now(UTC)
        self._stats = {"completed": 0, "failed": 0}

    async def submit_job(
        self,
        task_type: str,
        params: dict[str, Any],
        priority: int = 0,
    ) -> JobResponse:
        job_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        entry: dict[str, Any] = {
            "job_id": job_id,
            "task_type": task_type,
            "params": params,
            "status": "running",
            "priority": priority,
            "progress": 0,
            "result": None,
            "error_message": None,
            "created_at": now,
            "started_at": now,
            "finished_at": None,
        }
        self._jobs[job_id] = entry

        asyncio.create_task(self._execute_job(job_id, task_type, params))
        return JobResponse.model_validate(entry)

    async def _execute_job(
        self, job_id: str, task_type: str, params: dict[str, Any],
    ) -> None:
        entry = self._jobs[job_id]
        try:
            entry["progress"] = 50
            result = await self._run_task(task_type, params)
            entry["status"] = "completed"
            entry["progress"] = 100
            entry["result"] = result
            entry["finished_at"] = datetime.now(UTC).isoformat()
            self._stats["completed"] += 1
        except Exception as exc:
            entry["status"] = "failed"
            entry["error_message"] = str(exc)
            entry["finished_at"] = datetime.now(UTC).isoformat()
            self._stats["failed"] += 1

    async def _run_task(self, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
        if task_type == "crawl":
            return {"urls_crawled": 0, "note": "Crawl via scheduler in production"}
        if task_type == "reindex":
            return {"fragments_indexed": 0, "note": "Reindex via vector-indexer in production"}
        if task_type == "export":
            fmt = params.get("format", "json")
            return {"format": fmt, "note": "Export via export service in production"}
        if task_type == "cleanup":
            return {"removed": 0, "note": "Cleanup not yet implemented"}
        await asyncio.sleep(0.01)
        return {"result": f"Executed {task_type}"}

    async def get_job(self, job_id: str) -> JobResponse | None:
        entry = self._jobs.get(job_id)
        if not entry:
            return None
        return JobResponse.model_validate(entry)

    async def list_jobs(self, limit: int = 50) -> list[JobResponse]:
        sorted_jobs = sorted(
            self._jobs.values(),
            key=lambda j: (j["priority"], j["created_at"]),
            reverse=True,
        )
        return [JobResponse.model_validate(j) for j in sorted_jobs[:limit]]

    async def get_status(self) -> WorkerStatusResponse:
        active = sum(
            1 for j in self._jobs.values() if j["status"] == "running"
        )
        uptime = (datetime.now(UTC) - self._started_at).total_seconds()
        return WorkerStatusResponse(
            worker_id="default",
            active_jobs=active,
            completed_jobs=self._stats["completed"],
            failed_jobs=self._stats["failed"],
            uptime_seconds=uptime,
        )
