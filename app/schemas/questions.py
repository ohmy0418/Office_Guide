from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)


class QuestionResponse(BaseModel):
    """docs/specify.md 10.1 응답 필드."""

    request_id: UUID
    route_type: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    status: str
    sections: list[dict[str, Any]] = Field(default_factory=list)
    time_basis: dict[str, Any] | None = None
    partial_answer: bool | None = None
    failure_reason: str | None = None
