__anchor__ = "doc-check"

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.apps.doc_check.app.schemas.check import (
    CheckRequest,
    CheckResponse,
    JobStatusResponse,
)
from backend.apps.doc_check.app.services.check_service import DocCheckService

router = APIRouter(tags=["doc-check"])
_service = DocCheckService()


@router.post("/check", response_model=CheckResponse)
async def check_document(payload: CheckRequest) -> CheckResponse:
    return await _service.submit_check(
        tenant_id=payload.tenant_id,
        document_text=payload.document_text,
        document_title=payload.document_title,
        document_type=payload.document_type,
        subject_type=payload.subject_type,
    )


@router.get("/check/{job_id}", response_model=JobStatusResponse)
async def get_check_status(job_id: str) -> JobStatusResponse:
    result = await _service.get_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/check/{job_id}/stream")
async def stream_check_status(job_id: str) -> StreamingResponse:
    initial = await _service.get_job(job_id)
    if not initial:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream() -> AsyncIterator[str]:
        terminal = {"completed", "failed"}
        last_progress = -1
        for _ in range(60):
            job = await _service.get_job(job_id)
            if not job:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break

            progress = job.progress or 0
            if progress != last_progress:
                data = json.dumps({
                    "job_id": job_id,
                    "status": job.status,
                    "progress": progress,
                    "error_message": job.error_message,
                })
                yield f"data: {data}\n\n"
                last_progress = progress

            if job.status in terminal:
                if job.result:
                    result_data = json.dumps({
                        "job_id": job_id,
                        "status": job.status,
                        "progress": 100,
                        "result": {
                            "total_fragments_found": job.result.total_fragments_found,
                            "findings": [
                                {
                                    "finding_type": f.finding_type,
                                    "summary": f.summary,
                                    "confidence": f.confidence,
                                }
                                for f in (job.result.findings or [])
                            ],
                            "coverage_summary": job.result.coverage_summary,
                            "export_links": [
                                {"format": e.format, "url": e.url}
                                for e in (job.result.export_links or [])
                            ],
                        },
                    })
                    yield f"data: {result_data}\n\n"
                break

            await asyncio.sleep(1)
        else:
            yield f"data: {json.dumps({'status': 'timeout'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
