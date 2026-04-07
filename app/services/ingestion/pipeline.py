from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import DocumentStatus, ErrorCode, FailureReason
from app.db.models.document import Document
from app.db.models.document_chunk import DocumentChunk
from app.services.ingestion.chunking import count_tokens, merge_paragraphs_into_chunks
from app.services.ingestion.embedding import EmbeddingError, embed_texts
from app.services.ingestion.ocr import OcrFailedError, run_ocrmypdf
from app.services.ingestion.pdf_extract import extract_paragraphs_with_pages, needs_ocr

logger = logging.getLogger(__name__)


def run_ingestion(db: Session, document_id: uuid.UUID) -> None:
    doc = db.get(Document, document_id)
    if doc is None:
        return

    pdf_path = Path(doc.source_file_path)
    ocr_temp: Path | None = None
    try:
        if not pdf_path.is_file():
            _fail(
                db,
                doc,
                ErrorCode.INTERNAL_ERROR,
                "원본 파일을 찾을 수 없습니다.",
                FailureReason.PARSE_FAILED,
            )
            return

        work_path = pdf_path
        if needs_ocr(work_path):
            try:
                ocr_temp = run_ocrmypdf(work_path)
                work_path = ocr_temp
            except OcrFailedError as e:
                logger.exception("OCR 실패: %s", e)
                _fail(
                    db,
                    doc,
                    ErrorCode.OCR_FAILED,
                    str(e),
                    FailureReason.OCR_FAILED,
                    stderr=getattr(e, "stderr", None),
                )
                return

        paragraphs = extract_paragraphs_with_pages(work_path)
        if not paragraphs:
            _fail(
                db,
                doc,
                ErrorCode.PARSE_FAILED,
                "추출된 본문이 없습니다.",
                FailureReason.PARSE_FAILED,
            )
            return

        chunk_specs = merge_paragraphs_into_chunks(paragraphs)
        if not chunk_specs:
            _fail(
                db,
                doc,
                ErrorCode.PARSE_FAILED,
                "chunk를 생성하지 못했습니다.",
                FailureReason.PARSE_FAILED,
            )
            return

        texts = [c["content"] for c in chunk_specs]
        try:
            vectors = embed_texts(texts)
        except EmbeddingError as e:
            logger.exception("임베딩 실패: %s", e)
            _fail(
                db,
                doc,
                ErrorCode.EMBEDDING_FAILED,
                str(e),
                FailureReason.EMBEDDING_FAILED,
            )
            return
        except Exception as e:
            logger.exception("임베딩 API 오류")
            _fail(
                db,
                doc,
                ErrorCode.EMBEDDING_FAILED,
                str(e),
                FailureReason.EMBEDDING_FAILED,
            )
            return

        if len(vectors) != len(chunk_specs):
            _fail(
                db,
                doc,
                ErrorCode.EMBEDDING_FAILED,
                "임베딩 결과 개수가 chunk와 일치하지 않습니다.",
                FailureReason.EMBEDDING_FAILED,
            )
            return

        dim = len(vectors[0]) if vectors else 0
        if dim != settings.EMBEDDING_DIMENSION:
            _fail(
                db,
                doc,
                ErrorCode.EMBEDDING_FAILED,
                f"임베딩 차원이 설정(EMBEDDING_DIMENSION={settings.EMBEDDING_DIMENSION})과 다릅니다: {dim}",
                FailureReason.EMBEDDING_FAILED,
            )
            return

        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

        for order, (spec, vec) in enumerate(zip(chunk_specs, vectors, strict=True)):
            ch = DocumentChunk(
                chunk_id=uuid.uuid4(),
                document_id=document_id,
                chunk_order=order,
                heading=spec.get("heading"),
                heading_path=spec.get("heading_path"),
                article_ref=None,
                page_start=spec["page_start"],
                page_end=spec["page_end"],
                content=spec["content"],
                token_count=count_tokens(spec["content"]),
                embedding=vec,
            )
            db.add(ch)

        doc.status = DocumentStatus.COMPLETED.value
        doc.error_code = None
        doc.error_message = None
        doc.failure_reason = None
        db.commit()
    except Exception as e:
        logger.exception("인제스천 처리 중 오류")
        db.rollback()
        doc = db.get(Document, document_id)
        if doc:
            _fail(
                db,
                doc,
                ErrorCode.INTERNAL_ERROR,
                str(e),
                FailureReason.UNKNOWN,
            )
    finally:
        if ocr_temp is not None:
            ocr_temp.unlink(missing_ok=True)


def _fail(
    db: Session,
    doc: Document,
    code: ErrorCode,
    message: str,
    reason: FailureReason,
    stderr: str | None = None,
) -> None:
    doc.status = DocumentStatus.FAILED.value
    doc.error_code = code.value
    extra = f" {stderr}" if stderr else ""
    doc.error_message = (message + extra)[:10000]
    doc.failure_reason = reason.value
    db.commit()
