__anchor__ = "models"
# schema-ref: project-schema.yaml#/shared_modules/5

from enum import StrEnum


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class UserRole(StrEnum):
    ADMIN = "admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"


class SourceTier(StrEnum):
    TIER_1 = "1"
    TIER_2 = "2"
    TIER_3 = "3"


class DocumentStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnswerStatus(StrEnum):
    OK = "ok"
    REFUSED = "refused"
