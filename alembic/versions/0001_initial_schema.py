"""Initial schema: documents, document_chunks, query_logs, retrieval_eval_logs.

Embedding 차원은 EMBEDDING_DIMENSION(기본 1536)과 일치해야 한다.

Revision ID: 0001
Revises:
Create Date: 2026-04-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# docs/specify.md Phase 1 기본값과 .env.example 정렬
EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table(
        "documents",
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("document_type", sa.String(length=128), nullable=False),
        sa.Column("owner_department", sa.String(length=256), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("base_date", sa.Date(), nullable=True),
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_file_path", sa.Text(), nullable=False),
        sa.Column("source_file_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "document_chunks",
        sa.Column(
            "chunk_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.document_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_order", sa.Integer(), nullable=False),
        sa.Column("heading", sa.Text(), nullable=True),
        sa.Column("heading_path", sa.Text(), nullable=True),
        sa.Column("article_ref", sa.String(length=256), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
    )

    op.create_table(
        "query_logs",
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("user_id", sa.String(length=256), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("route_type", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "retrieval_eval_logs",
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("normalized_query", sa.Text(), nullable=True),
        sa.Column("keyword_query", sa.Text(), nullable=True),
        sa.Column("semantic_query", sa.Text(), nullable=True),
        sa.Column("metadata_filter", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("document_candidates", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("chunk_candidates", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("final_context_chunk_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("rerank_applied", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("retrieval_eval_logs")
    op.drop_table("query_logs")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.execute(sa.text("DROP EXTENSION IF EXISTS vector"))
