from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadMetadata(BaseModel):
    """업로드 시 함께 보내는 메타데이터 (docs/specify.md 9.1 참고)."""

    title: str = Field(..., min_length=1)
    document_type: str = Field(..., min_length=1)
    owner_department: str | None = None
    version: str | None = None
    effective_date: date | None = None
    base_date: date | None = None


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    document_status: str
    created_at: datetime


class DocumentIngestResponse(BaseModel):
    document_id: UUID
    document_status: str
    request_id: UUID


class DocumentStatusResponse(BaseModel):
    document_id: UUID
    document_status: str
    error_code: str | None = None
    error_message: str | None = None
    failure_reason: str | None = None
    updated_at: datetime
