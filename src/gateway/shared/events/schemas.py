__anchor__ = "events"
# schema-ref: project-schema.yaml#/shared_modules/6

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class EventType(StrEnum):
    DOCUMENT_DISCOVERED = "document.discovered"
    DOCUMENT_VERSION_CREATED = "document.version_created"
    FRAGMENT_INDEXED = "fragment.indexed"
    OBLIGATION_EXTRACTED = "obligation.extracted"
    ANSWER_COMPLETED = "answer.completed"
    ANSWER_REFUSED = "answer.refused"
    DOC_CHECK_COMPLETED = "doc_check.completed"
    USAGE_CHARGED = "usage.charged"
    CHANGE_DETECTED = "change.detected"


class OutboxEvent(BaseModel):
    event_id: UUID
    event_type: EventType
    aggregate_id: str
    payload: dict[str, object]
    created_at: datetime = datetime.now(UTC)
