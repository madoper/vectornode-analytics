__anchor__ = "models"

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy import Uuid as SA_Uuid
from sqlalchemy.dialects.postgresql import JSONB

from backend.shared.db.base import Base


class AuthUserModel(Base):
    __tablename__ = "users"

    id = Column(SA_Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(SA_Uuid, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class DocCheckJobModel(Base):
    __tablename__ = "doc_check_jobs"

    id = Column(SA_Uuid, primary_key=True, default=uuid.uuid4)
    internal_document_id = Column(SA_Uuid, nullable=True)
    tenant_id = Column(SA_Uuid, nullable=False)
    status = Column(String(50), nullable=False, default="queued")
    progress = Column(Integer, nullable=False, default=0)
    result_json = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class InternalDocumentModel(Base):
    __tablename__ = "internal_documents"

    id = Column(SA_Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(SA_Uuid, nullable=False)
    title = Column(String(512), nullable=False)
    document_type = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class SubjectProfileModel(Base):
    __tablename__ = "subject_profiles"

    id = Column(SA_Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(SA_Uuid, nullable=False)
    subject_type = Column(String(100), nullable=False)
    regulator = Column(String(255), nullable=True)
    extra_criteria = Column(JSONB, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class DraftModel(Base):
    __tablename__ = "drafts"

    id = Column(SA_Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(SA_Uuid, nullable=False)
    title = Column(String(512), nullable=False)
    draft_type = Column(String(100), nullable=False)
    content_json = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
