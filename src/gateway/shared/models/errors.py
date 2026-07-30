__anchor__ = "models"
# schema-ref: project-schema.yaml#/shared_modules/5


class PodFTError(Exception):
    """Base error for all pod-ft platform errors."""

    def __init__(self, code: str, message: str, details: dict[str, object] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InsufficientEvidenceError(PodFTError):
    def __init__(self) -> None:
        super().__init__(
            code="INSUFFICIENT_TIER1_EVIDENCE",
            message="Insufficient official cited fragments for a safe answer.",
        )


class TenantQuotaExceededError(PodFTError):
    def __init__(self) -> None:
        super().__init__(
            code="TENANT_QUOTA_EXCEEDED",
            message="Tenant monthly quota exceeded.",
        )


class AuthError(PodFTError):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(code="AUTH_FAILED", message=message)


class NotFoundError(PodFTError):
    def __init__(self, entity: str = "Resource") -> None:
        super().__init__(code="NOT_FOUND", message=f"{entity} not found.")
