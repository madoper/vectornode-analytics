__anchor__ = "scheduler"
# schema-ref: project-schema.yaml#/services/14

from typing import Any

from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    task_type: str = "crawl"
    cron_expr: str = "0 6 * * *"
    params: dict[str, Any] = Field(default_factory=dict)
    label: str = ""


class ScheduleResponse(BaseModel):
    schedule_id: str
    task_type: str
    cron_expr: str
    params: dict[str, Any]
    label: str
    enabled: bool
    last_run: str | None = None
    next_run: str | None = None
    created_at: str
    anchor: str = "scheduler"


class ScheduleHistoryItem(BaseModel):
    run_id: str
    schedule_id: str
    started_at: str
    finished_at: str | None = None
    status: str = "pending"
    result: str | None = None
    anchor: str = "scheduler"
