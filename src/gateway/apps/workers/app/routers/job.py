__anchor__ = "workers"
# schema-ref: project-schema.yaml#/services/15

from fastapi import APIRouter, HTTPException, Query

from backend.apps.workers.app.schemas.job import (
    JobResponse,
    JobSubmitRequest,
    WorkerStatusResponse,
)
from backend.apps.workers.app.services.worker_service import WorkerService

router = APIRouter(tags=["workers"])
_service = WorkerService()


@router.post("/workers/jobs", response_model=JobResponse, status_code=201)
async def submit_job(payload: JobSubmitRequest) -> JobResponse:
    return await _service.submit_job(
        task_type=payload.task_type,
        params=payload.params,
        priority=payload.priority,
    )


@router.get("/workers/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    result = await _service.get_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/workers/jobs", response_model=list[JobResponse])
async def list_jobs(limit: int = Query(50, ge=1, le=200)) -> list[JobResponse]:
    return await _service.list_jobs(limit=limit)


@router.get("/workers/status", response_model=WorkerStatusResponse)
async def worker_status() -> WorkerStatusResponse:
    return await _service.get_status()
