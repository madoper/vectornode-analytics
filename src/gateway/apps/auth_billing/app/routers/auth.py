__anchor__ = "auth-billing"

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from backend.apps.auth_billing.app.schemas.auth import (
    LoginRequest,
    ProfileResponse,
    QuotaCheckResponse,
    RegisterRequest,
    SubscriptionResponse,
    TokenResponse,
    UsageRecordRequest,
    UsageRecordResponse,
)
from backend.shared.db.postgres import async_session_factory
from backend.shared.repositories.repos import AuthUserRepository
from backend.shared.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["auth-billing"])
_users: dict[str, dict[str, Any]] = {}
_pg_available = True
# In-memory billing stores
_subscriptions: dict[str, dict[str, Any]] = {
    "1": {"tenant_id": "1", "tier": "free", "monthly_quota": 100},
    "demo": {"tenant_id": "demo", "tier": "free", "monthly_quota": 100},
}
_usage: dict[str, list[dict[str, Any]]] = {}


async def _try_repo() -> AuthUserRepository | None:
    global _pg_available
    if not _pg_available:
        return None
    try:
        session = async_session_factory()
        return AuthUserRepository(session)
    except Exception:
        _pg_available = False
        return None


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> dict[str, object]:
    repo = await _try_repo()
    if repo is not None:
        try:
            existing = await repo.list(email=payload.email)
            if existing:
                raise HTTPException(status_code=409, detail="Email already registered")
            user_id = uuid.uuid4()
            tenant_id = uuid.uuid4()
            await repo.create(
                id=user_id,
                tenant_id=tenant_id,
                email=payload.email,
                password_hash=hash_password(payload.password),
                role="user",
                is_active=True,
            )
            _subscriptions[str(tenant_id)] = {
                "tenant_id": str(tenant_id),
                "tier": "free",
                "monthly_quota": 100,
            }
            return {"user_id": str(user_id), "tenant_id": str(tenant_id), "anchor": "auth-billing"}
        except HTTPException:
            raise
        except Exception:
            _pg_available = False

    if payload.email in _users:
        raise HTTPException(status_code=409, detail="Email already registered")
    user_id = str(len(_users) + 1)
    _users[payload.email] = {
        "id": user_id,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "tenant_id": user_id,
    }
    return {"user_id": user_id, "tenant_id": user_id, "anchor": "auth-billing"}


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    repo = await _try_repo()
    user: dict[str, Any] | None = None
    if repo is not None:
        try:
            models = await repo.list(email=payload.email)
            if models:
                m = models[0]
                user = {
                    "id": str(m.id),
                    "email": m.email,
                    "password_hash": m.password_hash,
                    "tenant_id": str(m.tenant_id),
                }
        except Exception:
            _pg_available = False

    if not user:
        user = _users.get(payload.email)

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(subject=user["id"], tenant_id=user["tenant_id"])
    refresh_token = create_refresh_token(subject=user["id"])
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get("/auth/profile", response_model=ProfileResponse)
async def profile(_authorization: str = Depends(lambda: None)) -> ProfileResponse:
    return ProfileResponse(user_id="1", email="user@example.com", tenant_id="1", role="user")


@router.get("/billing/subscription/{tenant_id}", response_model=SubscriptionResponse)
async def get_subscription(tenant_id: str) -> SubscriptionResponse:
    sub = _subscriptions.get(tenant_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    current_month = datetime.now(UTC).strftime("%Y-%m")
    usage_records = _usage.get(tenant_id, [])
    usage_this_month = sum(
        r["tokens_used"]
        for r in usage_records
        if r.get("month", "").startswith(current_month)
    )
    quota = sub["monthly_quota"]
    return SubscriptionResponse(
        tenant_id=tenant_id,
        tier=sub["tier"],
        monthly_quota=quota,
        usage_this_month=usage_this_month,
        quota_remaining=max(0, quota - usage_this_month),
    )


@router.post("/billing/usage", response_model=UsageRecordResponse)
async def record_usage(payload: UsageRecordRequest) -> UsageRecordResponse:
    if payload.tenant_id not in _usage:
        _usage[payload.tenant_id] = []
    _usage[payload.tenant_id].append({
        "tenant_id": payload.tenant_id,
        "event_type": payload.event_type,
        "tokens_used": payload.tokens_used,
        "cost": payload.cost,
        "month": datetime.now(UTC).strftime("%Y-%m"),
        "created_at": datetime.now(UTC).isoformat(),
    })
    return UsageRecordResponse(recorded=True, event_type=payload.event_type)


@router.get("/billing/quota/{tenant_id}", response_model=QuotaCheckResponse)
async def check_quota(tenant_id: str) -> QuotaCheckResponse:
    sub = _subscriptions.get(tenant_id)
    if not sub:
        return QuotaCheckResponse(allowed=False, remaining=0, error_code="SUBSCRIPTION_NOT_FOUND")

    current_month = datetime.now(UTC).strftime("%Y-%m")
    usage_records = _usage.get(tenant_id, [])
    usage_this_month = sum(
        r["tokens_used"]
        for r in usage_records
        if r.get("month", "").startswith(current_month)
    )
    remaining = sub["monthly_quota"] - usage_this_month
    if remaining <= 0:
        return QuotaCheckResponse(allowed=False, remaining=0, error_code="TENANT_QUOTA_EXCEEDED")
    return QuotaCheckResponse(allowed=True, remaining=remaining)
