from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RetrievalEvalLog(Base):
    __tablename__ = "retrieval_eval_logs"

    request_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    normalized_query: Mapped[str | None] = mapped_column(Text(), nullable=True)
    keyword_query: Mapped[str | None] = mapped_column(Text(), nullable=True)
    semantic_query: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metadata_filter: Mapped[Any] = mapped_column(JSONB, nullable=True)
    document_candidates: Mapped[Any] = mapped_column(JSONB, nullable=True)
    chunk_candidates: Mapped[Any] = mapped_column(JSONB, nullable=True)
    final_context_chunk_ids: Mapped[Any] = mapped_column(JSONB, nullable=True)
    rerank_applied: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
