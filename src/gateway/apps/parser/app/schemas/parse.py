__anchor__ = "parser"
# schema-ref: project-schema.yaml#/services/4

from pydantic import BaseModel


class ParseHtmlRequest(BaseModel):
    url: str
    html_content: str
    document_title: str | None = None


class FragmentResponse(BaseModel):
    fragment_id: str
    fragment_no: int
    section_path: str | None = None
    paragraph_label: str | None = None
    fragment_text: str
    citation_label: str
    token_count: int
    anchor: str = "parser"


class ParseResultResponse(BaseModel):
    document_id: str
    document_title: str
    fragments: list[FragmentResponse]
    fragment_count: int
    anchor: str = "parser"
