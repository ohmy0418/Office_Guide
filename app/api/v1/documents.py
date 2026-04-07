from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.enums import DocumentStatus
from app.db.models.document import Document
from app.dependencies import get_db
from app.schemas.documents import (
    DocumentIngestResponse,
    DocumentStatusResponse,
    DocumentUploadMetadata,
    DocumentUploadResponse,
)
from app.services.ingestion.pipeline import run_ingestion
from app.services.storage import LocalStorageService

router = APIRouter()


def get_storage() -> LocalStorageService:
    return LocalStorageService()


def _run_ingest_job(document_id: uuid.UUID) -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        run_ingestion(db, document_id)
    finally:
        db.close()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form(..., description="JSON 문자열 (DocumentUploadMetadata)"),
    db: Session = Depends(get_db),
    storage: LocalStorageService = Depends(get_storage),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "파일 이름이 없습니다.")

    raw = await file.read()
    if len(raw) < 5 or not raw[:5].startswith(b"%PDF"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "PDF 파일만 업로드할 수 있습니다.")

    try:
        meta = DocumentUploadMetadata.model_validate_json(metadata)
    except Exception as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"metadata JSON이 올바르지 않습니다: {e}",
        ) from e

    document_id = uuid.uuid4()
    safe_name = file.filename or "document.pdf"
    path = storage.save_bytes(document_id, safe_name, raw)

    doc = Document(
        document_id=document_id,
        title=meta.title,
        document_type=meta.document_type,
        owner_department=meta.owner_department,
        version=meta.version,
        effective_date=meta.effective_date,
        base_date=meta.base_date,
        is_latest=True,
        source_file_path=path,
        source_file_type="PDF",
        status=DocumentStatus.PENDING.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentUploadResponse(
        document_id=document_id,
        document_status=doc.status,
        created_at=doc.created_at,
    )


@router.post("/{document_id}/ingest", response_model=DocumentIngestResponse)
def start_ingest(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> DocumentIngestResponse:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "문서를 찾을 수 없습니다.")

    if doc.status == DocumentStatus.PROCESSING.value:
        raise HTTPException(status.HTTP_409_CONFLICT, "이미 반영 처리 중입니다.")

    allowed = {
        DocumentStatus.PENDING.value,
        DocumentStatus.FAILED.value,
        DocumentStatus.REINDEX_REQUIRED.value,
    }
    if doc.status not in allowed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"현재 상태에서 반영을 시작할 수 없습니다: {doc.status}",
        )

    request_id = uuid.uuid4()
    doc.status = DocumentStatus.PROCESSING.value
    doc.error_code = None
    doc.error_message = None
    doc.failure_reason = None
    db.commit()

    background_tasks.add_task(_run_ingest_job, document_id)

    return DocumentIngestResponse(
        document_id=document_id,
        document_status=doc.status,
        request_id=request_id,
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DocumentStatusResponse:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "문서를 찾을 수 없습니다.")

    return DocumentStatusResponse(
        document_id=doc.document_id,
        document_status=doc.status,
        error_code=doc.error_code,
        error_message=doc.error_message,
        failure_reason=doc.failure_reason,
        updated_at=doc.updated_at,
    )
