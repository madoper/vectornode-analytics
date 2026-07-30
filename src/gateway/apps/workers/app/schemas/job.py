__anchor__ = "workers"
# schema-ref: project-schema.yaml#/services/15

from typing import Any

from pydantic import BaseModel, Field


class JobSubmitRequest(BaseModel):
    task_type: str = "crawl"
    params: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0


class JobResponse(BaseModel):
    job_id: str
    task_type: str
    params: dict[str, Any]
    status: str = "pending"
    priority: int = 0
    progress: int = 0
    result: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    anchor: str = "workers"


class WorkerStatusResponse(BaseModel):
    worker_id: str
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    uptime_seconds: float
    anchor: str = "workers"
