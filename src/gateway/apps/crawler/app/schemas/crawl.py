__anchor__ = "crawler"
# schema-ref: project-schema.yaml#/services/3

from pydantic import BaseModel


class StartCrawlRequest(BaseModel):
    source_domain: str
    url: str
    crawl_depth: int = 1


class CrawlJobResponse(BaseModel):
    job_id: str
    status: str
    source_domain: str
    anchor: str = "crawler"


class CrawlResultResponse(BaseModel):
    result_id: str
    url: str
    content_type: str
    checksum: str
    anchor: str = "crawler"
