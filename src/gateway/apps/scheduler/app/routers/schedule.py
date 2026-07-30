__anchor__ = "scheduler"
# schema-ref: project-schema.yaml#/services/14

from fastapi import APIRouter, HTTPException

from backend.apps.scheduler.app.schemas.schedule import (
    ScheduleHistoryItem,
    ScheduleRequest,
    ScheduleResponse,
)
from backend.apps.scheduler.app.services.scheduler_service import SchedulerService

router = APIRouter(tags=["scheduler"])
_service = SchedulerService()


@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedule(payload: ScheduleRequest) -> ScheduleResponse:
    return await _service.create_schedule(
        task_type=payload.task_type,
        cron_expr=payload.cron_expr,
        params=payload.params,
        label=payload.label,
    )


@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules() -> list[ScheduleResponse]:
    return await _service.list_schedules()


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: str) -> ScheduleResponse:
    result = await _service.get_schedule(schedule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return result


@router.delete("/schedules/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: str) -> None:
    if not await _service.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")


@router.get("/schedules/{schedule_id}/history", response_model=list[ScheduleHistoryItem])
async def get_schedule_history(schedule_id: str) -> list[ScheduleHistoryItem]:
    return await _service.get_schedule_history(schedule_id)


@router.post("/schedules/tick", response_model=list[ScheduleHistoryItem])
async def tick_schedules() -> list[ScheduleHistoryItem]:
    """Manually trigger due schedules. Called by cron or external scheduler."""
    return await _service.execute_due()
