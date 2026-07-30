__anchor__ = "crawler"
# schema-ref: project-schema.yaml#/services/3

from fastapi import APIRouter, HTTPException

from backend.apps.crawler.app.schemas.crawl import (
    CrawlJobResponse,
    CrawlResultResponse,
    StartCrawlRequest,
)
from backend.apps.crawler.app.services.crawler_service import CrawlerService

router = APIRouter(tags=["crawler"])
_crawler_service = CrawlerService()


@router.post("/crawl", status_code=201, response_model=CrawlJobResponse)
async def start_crawl(payload: StartCrawlRequest) -> CrawlJobResponse:
    job = await _crawler_service.start_crawl(
        source_domain=payload.source_domain,
        url=payload.url,
        crawl_depth=payload.crawl_depth,
    )
    return CrawlJobResponse(
        job_id=job["id"],
        status=job["status"],
        source_domain=job["source_domain"],
        anchor="crawler",
    )


@router.get("/crawl/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_status(job_id: str) -> CrawlJobResponse:
    job = await _crawler_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return CrawlJobResponse(
        job_id=job["id"],
        status=job["status"],
        source_domain=job["source_domain"],
        anchor="crawler",
    )


@router.get("/crawl/{job_id}/results", response_model=list[CrawlResultResponse])
async def get_crawl_results(job_id: str) -> list[CrawlResultResponse]:
    results = await _crawler_service.get_results(job_id)
    return [
        CrawlResultResponse(
            result_id=r["id"],
            url=r["url"],
            content_type=r["content_type"],
            checksum=r["checksum"],
            anchor="crawler",
        )
        for r in results
    ]
