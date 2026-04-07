from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.document import Document


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    heading: Mapped[str | None] = mapped_column(Text(), nullable=True)
    heading_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    article_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    document: Mapped[Document] = relationship("Document", back_populates="chunks")
