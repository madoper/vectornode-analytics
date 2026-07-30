__anchor__ = "auth-billing"
# schema-ref: project-schema.yaml#/services/1

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    tenant_id: str
    role: str
    anchor: str = "auth-billing"


class SubscriptionResponse(BaseModel):
    tenant_id: str
    tier: str
    monthly_quota: int
    usage_this_month: int
    quota_remaining: int
    anchor: str = "auth-billing"


class UsageRecordRequest(BaseModel):
    tenant_id: str
    event_type: str
    tokens_used: int = 0
    cost: float = 0.0


class UsageRecordResponse(BaseModel):
    recorded: bool
    event_type: str
    anchor: str = "auth-billing"


class QuotaCheckResponse(BaseModel):
    allowed: bool
    remaining: int
    error_code: str | None = None
    anchor: str = "auth-billing"
