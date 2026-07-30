__anchor__ = "answer-service"
# schema-ref: project-schema.yaml#/services/10

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.apps.answer_service.app.schemas.answer import (
    AnswerDto,
    AnswerQuestionRequest,
    AnswerQuestionResponse,
)
from backend.apps.answer_service.app.services.answering_service import AnsweringService

router = APIRouter(tags=["questions"])
_service = AnsweringService()


@router.post("/answer", response_model=AnswerQuestionResponse)
async def answer_question(payload: AnswerQuestionRequest) -> AnswerQuestionResponse:
    result = await _service.answer(
        question=payload.question,
        channel=payload.channel,
        subject_type=payload.subject_type,
        regulator=payload.regulator,
        as_of_date=payload.as_of_date,
    )
    return AnswerQuestionResponse(
        answer_session_id=result["session_id"],
        status=result["status"],
        answer=AnswerDto(**result["answer"]) if result.get("answer") else None,
        reason_code=result.get("reason_code"),
        evidence_count=result.get("evidence_count", 0),
        verifier_status=result.get("verifier_status"),
        anchor="answer-service",
    )


@router.get("/answer/{session_id}", response_model=AnswerQuestionResponse)
async def get_answer_status(session_id: str) -> AnswerQuestionResponse:
    result = await _service.get_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return AnswerQuestionResponse(
        answer_session_id=result["session_id"],
        status=result["status"],
        answer=AnswerDto(**result["answer"]) if result.get("answer") else None,
        reason_code=result.get("reason_code"),
        evidence_count=result.get("evidence_count", 0),
        verifier_status=result.get("verifier_status"),
        anchor="answer-service",
    )


@router.get("/answer/{session_id}/stream")
async def answer_stream(session_id: str) -> StreamingResponse:
    result = await _service.get_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")

    if result["status"] == "refused":
        async def refuse_stream() -> AsyncGenerator[str, None]:
            err = json.dumps({'type': 'error', 'reason_code': result.get('reason_code')})
            yield f"data: {err}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(refuse_stream(), media_type="text/event-stream")

    answer = result.get("answer")
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not yet ready")

    summary = answer.get("summary", "")
    citations = answer.get("citations", [])
    llm_summary = answer.get("llm_summary")

    async def event_stream() -> AsyncGenerator[str, None]:
        if llm_summary:
            yield f"data: {json.dumps({'type': 'summary', 'text': llm_summary})}\n\n"
            await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'type': 'citations', 'citations': citations})}\n\n"
        await asyncio.sleep(0.1)

        chunk_size = 20
        for i in range(0, len(summary), chunk_size):
            chunk = summary[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'token', 'text': chunk})}\n\n"
            await asyncio.sleep(0.02)

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

