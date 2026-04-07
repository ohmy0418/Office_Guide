from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.enums import ErrorCode, QueryStatus, RouteType
from app.db.models.query_log import QueryLog
from app.dependencies import get_db
from app.schemas.questions import QuestionRequest, QuestionResponse
from app.services.question.analyze import analyze_question

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse)
def post_question(payload: QuestionRequest, db: Session = Depends(get_db)) -> QuestionResponse:
    t0 = time.perf_counter()
    analysis = analyze_question(payload.question)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    err_code = None
    err_msg = None
    fail_reason = analysis.failure_reason
    if analysis.status == QueryStatus.FALLBACK and analysis.route_type == RouteType.UNSUPPORTED:
        err_code = ErrorCode.ROUTING_FAILED.value
        err_msg = "라우팅 실패(처리 불가 유형)"

    log = QueryLog(
        request_id=analysis.request_id,
        user_id=payload.user_id,
        question=payload.question,
        route_type=analysis.route_type.value,
        status=analysis.status.value,
        latency_ms=latency_ms,
        error_code=err_code,
        error_message=err_msg,
        failure_reason=fail_reason,
    )
    db.add(log)
    db.commit()

    return QuestionResponse(
        request_id=analysis.request_id,
        route_type=analysis.route_type.value,
        answer=analysis.answer,
        sources=[],
        status=analysis.status.value,
        sections=analysis.sections,
        time_basis=analysis.time_basis,
        partial_answer=analysis.partial_answer,
        failure_reason=analysis.failure_reason,
    )
