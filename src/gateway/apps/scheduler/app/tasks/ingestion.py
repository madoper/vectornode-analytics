__anchor__ = "scheduler"

from datetime import UTC, datetime
from typing import Any

from backend.shared.logging import logger


async def run_ingestion(params: dict[str, Any] | None = None) -> dict[str, Any]:
    _ = params
    started_at = datetime.now(UTC)

    # Step 1: get active source domains from source-registry
    try:
        from backend.apps.source_registry.app.services.sources_service import (
            SourcesService,
        )
        src_service = SourcesService()
        sources = await src_service.list_sources()
        active_sources = [s for s in sources if s.get("is_active", False)]
        logger.info("ingestion: found %d active sources", len(active_sources))
    except Exception as exc:
        logger.error("ingestion: failed to fetch sources: %s", exc)
        return {"status": "error", "step": "source-registry", "error": str(exc)}

    results = []
    for source in active_sources:
        source_result = await _process_source(source)
        results.append(source_result)

    elapsed = (datetime.now(UTC) - started_at).total_seconds()
    return {
        "status": "completed",
        "sources_processed": len(results),
        "results": results,
        "elapsed_seconds": elapsed,
    }


async def _process_source(source: dict[str, Any]) -> dict[str, Any]:
    source_domain = source.get("domain", "")
    logger.info("ingestion: processing source %s", source_domain)

    # Step 2: crawl
    try:
        from backend.apps.crawler.app.services.crawler_service import CrawlerService
        crawler = CrawlerService()
        job = await crawler.start_crawl(
            source_domain=source_domain,
            url=source.get("base_url", f"https://{source_domain}"),
            crawl_depth=1,
        )
        if job.get("status") == "error":
            return {"source": source_domain, "status": "error", "step": "crawler"}
        results = await crawler.get_results(job["id"])
        logger.info("ingestion: crawled %d pages from %s", len(results), source_domain)
    except Exception as exc:
        logger.error("ingestion: crawl failed for %s: %s", source_domain, exc)
        return {"source": source_domain, "status": "error", "step": "crawler"}

    # Step 3: parse + version + extract for each result
    pages_processed = 0
    for crawl_result in results:
        try:
            await _process_crawl_result(crawl_result, source_domain)
            pages_processed += 1
        except Exception as exc:
            logger.warning("ingestion: skip %s: %s", crawl_result.get("url"), exc)
            continue

    return {
        "source": source_domain,
        "status": "completed",
        "pages_crawled": len(results),
        "pages_processed": pages_processed,
    }


async def _process_crawl_result(
    crawl_result: dict[str, Any], source_domain: str
) -> None:
    from backend.apps.obligation_extractor.app.services.extractor_service import (
        ObligationExtractorService,
    )
    from backend.apps.parser.app.services.parse_service import ParseService
    from backend.apps.retrieval.app.services.retrieval_service import RetrievalService
    from backend.apps.vector_indexer.app.services.indexer_service import IndexerService
    from backend.apps.versioning.app.services.versioning_service import (
        VersioningService,
    )

    url = crawl_result.get("url", "")
    content = crawl_result.get("content", "")
    title = crawl_result.get("title", "")

    # Parse
    parser = ParseService()
    parsed = await parser.parse_html(url=url, html_content=content, document_title=title)
    if not parsed or not parsed.get("fragments"):
        logger.warning("ingestion: parse returned empty for %s", url)
        return

    # Register version
    versioner = VersioningService()
    content_hash = crawl_result.get("checksum", "")
    version_result = await versioner.register_document(
        canonical_url=url,
        document_title=parsed.get("document_title", title),
        document_kind="unknown",
        content_hash=content_hash,
        regulator_code=_get_regulator_code(source_domain),
    )

    # Extract obligations
    extractor = ObligationExtractorService()
    fragments = parsed.get("fragments", [])
    extraction = await extractor.extract(
        document_id=version_result["document_id"],
        document_version_id=version_result["version_id"],
        fragments=fragments,
    )

    # Index into BM25 (always works, in-memory)
    retrieval = RetrievalService()
    enriched_fragments = _enrich_fragments(
        fragments, version_result, source_domain
    )
    bm25_count = await retrieval.index_fragments(enriched_fragments)
    logger.info("ingestion: indexed %d fragments in BM25 for %s", bm25_count, url)

    # Index vectors into Qdrant (optional, gracefully degrades if not available)
    indexer = IndexerService()
    qdrant_count = await indexer.index_fragments(enriched_fragments)
    if qdrant_count > 0:
        logger.info("ingestion: indexed %d vectors in Qdrant for %s", qdrant_count, url)
    else:
        logger.info("ingestion: Qdrant not available, skipped vector indexing for %s", url)

    logger.info(
        "ingestion: processed %s — norms=%d, obligations=%d, fragments=%d",
        url,
        extraction.get("norm_count", 0),
        extraction.get("obligation_count", 0),
        len(fragments),
    )


def _get_regulator_code(domain: str) -> str:
    mapping = {
        "fedsfm.ru": "rosfinmonitoring",
        "cbr.ru": "cbr",
        "minfin.gov.ru": "minfin",
        "consultant.ru": "consultant",
        "garant.ru": "garant",
    }
    for key, value in mapping.items():
        if key in domain:
            return value
    return "unknown"


def _enrich_fragments(
    fragments: list[dict[str, Any]],
    version_result: dict[str, Any],
    source_domain: str,
) -> list[dict[str, Any]]:
    enriched = []
    for f in fragments:
        f["document_id"] = version_result.get("document_id")
        f["document_version_id"] = version_result.get("version_id")
        f["source_domain"] = source_domain
        f["tier"] = 1
        f["is_current"] = version_result.get("is_current", True)
        enriched.append(f)
    return enriched
