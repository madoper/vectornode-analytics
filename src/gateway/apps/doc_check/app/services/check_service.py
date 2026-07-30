__anchor__ = "doc-check"

import asyncio
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from backend.apps.doc_check.app.schemas.check import (
    CheckResponse,
    ExportLink,
    Finding,
    JobStatusResponse,
)
from backend.apps.retrieval.app.services.retrieval_service import RetrievalService
from backend.apps.verification.app.services.sufficiency_policy import SufficiencyPolicy
from backend.shared.db.postgres import async_session_factory
from backend.shared.repositories.repos import DocCheckJobRepository


class DocCheckService:
    def __init__(self) -> None:
        self._retrieval = RetrievalService()
        self._policy = SufficiencyPolicy()
        self._jobs: dict[str, dict[str, Any]] = {}
        self._pg_available = True

    async def _try_pg(self) -> DocCheckJobRepository | None:
        if not self._pg_available:
            return None
        try:
            session = async_session_factory()
            return DocCheckJobRepository(session)
        except Exception:
            self._pg_available = False
            return None

    async def submit_check(  # noqa: PLR0913
        self,
        tenant_id: str,
        document_text: str,
        document_title: str,  # noqa: ARG002
        document_type: str = "internal_policy",  # noqa: ARG002
        subject_type: str | None = None,
    ) -> CheckResponse:
        job_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        repo = await self._try_pg()
        if repo is not None:
            try:
                await repo.create(
                    id=uuid.UUID(job_id),
                    tenant_id=uuid.UUID(tenant_id) if _is_uuid(tenant_id) else None,
                    status="pending",
                    progress=0,
                )
            except Exception:
                self._pg_available = False
                repo = None

        if repo is None:
            entry: dict[str, Any] = {
                "status": "pending",
                "progress": 0,
                "result": None,
                "error_message": None,
                "created_at": now,
            }
            self._jobs[job_id] = entry

        asyncio.create_task(self._execute_check(
            job_id=job_id,
            document_text=document_text,
            subject_type=subject_type,
        ))

        return CheckResponse(
            job_id=job_id,
            status="pending",
            total_fragments_found=0,
            findings=[],
            coverage_summary="Check submitted, processing...",
            created_at=now,
        )

    async def _execute_check(
        self,
        job_id: str,
        document_text: str,
        subject_type: str | None = None,
    ) -> None:
        repo = await self._try_pg()
        try:
            if repo is not None:
                await repo.update(job_id, status="running", progress=10)
            elif job_id in self._jobs:
                self._jobs[job_id]["status"] = "running"
                self._jobs[job_id]["progress"] = 10

            fragments = await self._retrieval.search(
                query=document_text,
                subject_type=subject_type,
                top_k=20,
            )

            if repo is not None:
                await repo.update(job_id, progress=50)
            elif job_id in self._jobs:
                self._jobs[job_id]["progress"] = 50

            decision = self._policy.evaluate_fragments(fragments)

            if repo is not None:
                await repo.update(job_id, progress=80)
            elif job_id in self._jobs:
                self._jobs[job_id]["progress"] = 80

            findings: list[Finding] = []
            if not decision.allowed:
                findings.append(Finding(
                    finding_type="insufficient_coverage",
                    summary=(
                        f"Document does not meet regulatory evidence threshold:"
                        f" {decision.reason_code}"
                    ),
                    confidence=0.0,
                ))

            for f in fragments[:10]:
                findings.append(Finding(
                    finding_type="matched_fragment",
                    summary="Relevant regulatory requirement found",
                    citation_label=f.get("citation_label"),
                    fragment_text=f.get("fragment_text", "")[:200],
                    confidence=f.get("confidence", 0),
                ))

            if not findings:
                findings.append(Finding(
                    finding_type="no_regulatory_match",
                    summary="No applicable regulatory fragments found for this document",
                    confidence=0.0,
                ))

            if decision.allowed:
                coverage = (
                    f"Found {len(fragments)} relevant Tier-1 fragments."
                    f" Document coverage meets sufficiency threshold."
                )
            else:
                coverage = (
                    f"Found {len(fragments)} relevant fragments but insufficient:"
                    f" {decision.reason_code}. Consider revising document."
                )

            base_url = f"/api/v1/export?job_id={job_id}&format="
            export_links = [
                ExportLink(format="json", url=f"{base_url}json", label="JSON"),
                ExportLink(format="docx", url=f"{base_url}docx", label="DOCX"),
                ExportLink(format="pdf", url=f"{base_url}pdf", label="PDF"),
                ExportLink(format="xlsx", url=f"{base_url}xlsx", label="XLSX"),
            ]

            result = CheckResponse(
                job_id=job_id,
                status="completed",
                total_fragments_found=len(fragments),
                findings=findings,
                coverage_summary=coverage,
                created_at=datetime.now(UTC).isoformat(),
                export_links=export_links,
            )

            if repo is not None:
                await repo.update(
                    job_id,
                    status="completed",
                    progress=100,
                    result_json=json.loads(result.model_dump_json()),
                )
            elif job_id in self._jobs:
                entry = self._jobs[job_id]
                entry["status"] = "completed"
                entry["progress"] = 100
                entry["result"] = result

        except Exception as exc:
            if repo is not None:
                await repo.update(job_id, status="failed", error_message=str(exc))
            elif job_id in self._jobs:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error_message"] = str(exc)

    async def get_job(self, job_id: str) -> JobStatusResponse | None:
        repo = await self._try_pg()
        if repo is not None:
            try:
                model = await repo.get(job_id)
                if model is not None:
                    result = None
                    if model.result_json and model.status == "completed":
                        result = CheckResponse(**model.result_json)
                    return JobStatusResponse(
                        job_id=job_id,
                        status=model.status,
                        progress=model.progress,
                        result=result,
                        error_message=model.error_message,
                    )
            except Exception:
                self._pg_available = False

        job = self._jobs.get(job_id)
        if not job:
            return None
        return JobStatusResponse(
            job_id=job_id,
            status=job["status"],
            progress=job.get("progress", 0),
            result=job.get("result"),
            error_message=job.get("error_message"),
        )


def _is_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False
