__anchor__ = "scheduler"
# schema-ref: project-schema.yaml#/services/14

import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.scheduler.app.schemas.schedule import (
    ScheduleHistoryItem,
    ScheduleResponse,
)
from backend.shared.logging import logger


class SchedulerService:
    """Manages periodic task schedules.

    Uses in-memory store for Sprint 4. In Sprint 5+ this will use Redis
    for persistence and APScheduler for actual cron execution.
    """

    def __init__(self) -> None:
        self._schedules: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._init_default_schedules()

    def _init_default_schedules(self) -> None:
        defaults: list[tuple[str, str, dict[str, Any], str]] = [
            ("ingestion", "0 6 * * *", {}, "Daily regulatory ingestion at 6 AM"),
            ("healthcheck", "*/30 * * * *", {}, "Healthcheck every 30 min"),
        ]
        for task_type, cron_expr, params, label in defaults:
            sid = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()
            self._schedules[sid] = {
                "schedule_id": sid,
                "task_type": task_type,
                "cron_expr": cron_expr,
                "params": params,
                "label": label,
                "enabled": True,
                "last_run": None,
                "next_run": self._estimate_next_run(cron_expr),
                "created_at": now,
            }
            self._history[sid] = []
            logger.info("scheduler: created default schedule %s (%s)", label, sid)

    async def create_schedule(
        self,
        task_type: str,
        cron_expr: str,
        params: dict[str, Any],
        label: str,
    ) -> ScheduleResponse:
        schedule_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        entry = {
            "schedule_id": schedule_id,
            "task_type": task_type,
            "cron_expr": cron_expr,
            "params": params,
            "label": label,
            "enabled": True,
            "last_run": None,
            "next_run": self._estimate_next_run(cron_expr),
            "created_at": now,
        }
        self._schedules[schedule_id] = entry
        self._history[schedule_id] = []
        return ScheduleResponse.model_validate(entry)

    async def list_schedules(self) -> list[ScheduleResponse]:
        return [ScheduleResponse.model_validate(s) for s in self._schedules.values()]

    async def get_schedule(self, schedule_id: str) -> ScheduleResponse | None:
        entry = self._schedules.get(schedule_id)
        if not entry:
            return None
        return ScheduleResponse.model_validate(entry)

    async def delete_schedule(self, schedule_id: str) -> bool:
        if schedule_id not in self._schedules:
            return False
        del self._schedules[schedule_id]
        self._history.pop(schedule_id, None)
        return True

    async def get_schedule_history(
        self, schedule_id: str,
    ) -> list[ScheduleHistoryItem]:
        items = self._history.get(schedule_id, [])
        return [ScheduleHistoryItem.model_validate(h) for h in items]

    async def execute_due(self) -> list[ScheduleHistoryItem]:
        now = datetime.now(UTC)
        now_str = now.isoformat()
        executed: list[ScheduleHistoryItem] = []
        for sid, entry in list(self._schedules.items()):
            if not entry["enabled"]:
                continue
            next_run = entry.get("next_run")
            if next_run and next_run > now_str:
                continue
            run_id = str(uuid.uuid4())
            item: dict[str, Any] = {
                "run_id": run_id,
                "schedule_id": sid,
                "started_at": now_str,
                "finished_at": now_str,
                "status": "running",
                "result": None,
            }
            try:
                raw = await _execute_task(entry["task_type"], entry.get("params", {}))
                result = str(raw) if not isinstance(raw, str) else raw
                item["status"] = "completed"
                item["result"] = result
            except Exception as exc:
                logger.error("scheduler: task %s failed: %s", entry["task_type"], exc)
                item["status"] = "error"
                item["result"] = str(exc)
            item["finished_at"] = datetime.now(UTC).isoformat()
            self._history.setdefault(sid, []).append(item)
            entry["last_run"] = now_str
            entry["next_run"] = self._estimate_next_run(entry["cron_expr"])
            executed.append(ScheduleHistoryItem.model_validate(item))
        return executed

    @staticmethod
    def _estimate_next_run(cron_expr: str) -> str:
        from datetime import timedelta
        parts = cron_expr.split()
        if len(parts) < 2:
            return datetime.now(UTC).isoformat()
        hour = int(parts[1]) if parts[1].isdigit() else 0
        minute = int(parts[0]) if parts[0].isdigit() else 0
        now = datetime.now(UTC)
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.isoformat()


async def _execute_task(task_type: str, params: dict[str, Any]) -> dict[str, Any]:
    if task_type == "ingestion":
        from backend.apps.scheduler.app.tasks.ingestion import run_ingestion
        return await run_ingestion(params)
    if task_type == "crawl":
        from backend.apps.crawler.app.services.crawler_service import CrawlerService
        svc = CrawlerService()
        url = params.get("url", "")
        source_domain = params.get("source_domain", "unknown")
        job = await svc.start_crawl(source_domain=source_domain, url=url, crawl_depth=1)
        return {"job_id": job["id"], "status": job["status"]}
    if task_type == "reindex":
        _ = params.get("collection")
        return {"status": "completed"}
    if task_type == "healthcheck":
        svcs = ["crawler", "parser", "versioning", "extractor", "indexer"]
        return {"status": "ok", "services": svcs}
    return {"status": "skipped", "message": f"Unknown task type: {task_type}"}
