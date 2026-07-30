__anchor__ = "parser"
# schema-ref: project-schema.yaml#/services/4

from fastapi import APIRouter

from backend.apps.parser.app.schemas.parse import (
    FragmentResponse,
    ParseHtmlRequest,
    ParseResultResponse,
)
from backend.apps.parser.app.services.parse_service import ParseService

router = APIRouter(tags=["parser"])
_parse_service = ParseService()


@router.post("/parse/html", response_model=ParseResultResponse)
async def parse_html(payload: ParseHtmlRequest) -> ParseResultResponse:
    result = await _parse_service.parse_html(
        url=payload.url,
        html_content=payload.html_content,
        document_title=payload.document_title,
    )
    return ParseResultResponse(
        document_id=result["document_id"],
        document_title=result["document_title"],
        fragments=[FragmentResponse(**f) for f in result["fragments"]],
        fragment_count=result["fragment_count"],
        anchor="parser",
    )
