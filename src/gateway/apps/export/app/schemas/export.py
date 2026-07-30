__anchor__ = "export"
# schema-ref: project-schema.yaml#/services/14

from pydantic import BaseModel


class ExportSection(BaseModel):
    title: str
    content: str
    citations: list[str] = []


class ExportRequest(BaseModel):
    format: str = "json"
    title: str = "Report"
    sections: list[ExportSection] = []
    summary: str | None = None


class ExportResponse(BaseModel):
    format: str
    filename: str
    content_type: str
    data: str
    anchor: str = "export"
