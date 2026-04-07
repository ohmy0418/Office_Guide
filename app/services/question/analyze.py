from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.core.enums import FailureReason, QueryStatus, RouteType
from app.services.question.extraction import ExtractedEntities, extract_entities
from app.services.question.llm_router import maybe_refine_route
from app.services.question.normalize import normalize_question
from app.services.question.rules_router import classify_route


@dataclass
class QuestionAnalysis:
    request_id: uuid.UUID
    normalized_question: str
    entities: ExtractedEntities
    route_type: RouteType
    routing_confidence: float
    routing_scores: dict[str, float]
    used_retry: bool
    status: QueryStatus
    failure_reason: str | None
    metadata_filters: dict[str, Any]
    db_params: dict[str, Any]
    answer: str
    sections: list[dict[str, Any]]
    time_basis: dict[str, Any] | None = None
    partial_answer: bool = False


def _build_filters(entities: ExtractedEntities) -> dict[str, Any]:
    return {
        "document_title_keywords": entities.document_hints[:10],
        "time_expressions": entities.time_expressions,
    }


def _build_db_params(entities: ExtractedEntities) -> dict[str, Any]:
    return {
        "person_names": entities.person_names,
        "departments": entities.departments,
        "emails": entities.emails,
        "phones": entities.phones,
    }


def _time_basis(entities: ExtractedEntities) -> dict[str, Any] | None:
    if not entities.time_expressions:
        return None
    return {"expressions": entities.time_expressions}


def _answer_stub(route: RouteType) -> str:
    if route == RouteType.UNSUPPORTED:
        return "질문을 서비스 범위에서 처리할 수 있는 유형으로 분류하지 못했습니다. Phase 4 이후 검색·조회와 연동됩니다."
    if route == RouteType.RAG:
        return "문서 검색(RAG) 경로로 분류되었습니다. 이후 단계에서 검색·답변 생성이 수행됩니다."
    if route == RouteType.DB_API:
        return "정형 조회 경로로 분류되었습니다. 이후 단계에서 사전 정의 SQL/API 조회가 수행됩니다."
    return "혼합 조회 경로로 분류되었습니다. 문서 근거와 정형 데이터를 병합하는 단계는 이후 구현됩니다."


def analyze_question(question: str) -> QuestionAnalysis:
    request_id = uuid.uuid4()
    raw = question.strip()
    if len(raw) < 2:
        return QuestionAnalysis(
            request_id=request_id,
            normalized_question=raw,
            entities=ExtractedEntities(),
            route_type=RouteType.UNSUPPORTED,
            routing_confidence=0.0,
            routing_scores={},
            used_retry=False,
            status=QueryStatus.FALLBACK,
            failure_reason=FailureReason.ROUTING_FAILED.value,
            metadata_filters={},
            db_params={},
            answer=_answer_stub(RouteType.UNSUPPORTED),
            sections=[],
            time_basis=None,
            partial_answer=False,
        )

    normalized = normalize_question(raw)
    entities = extract_entities(normalized)
    result = classify_route(normalized, entities)

    refined = maybe_refine_route(normalized, entities, result.route_type)
    route = refined if refined is not None else result.route_type

    if route == RouteType.UNSUPPORTED:
        return QuestionAnalysis(
            request_id=request_id,
            normalized_question=normalized,
            entities=entities,
            route_type=RouteType.UNSUPPORTED,
            routing_confidence=result.confidence,
            routing_scores=result.scores,
            used_retry=result.used_retry,
            status=QueryStatus.FALLBACK,
            failure_reason=FailureReason.ROUTING_FAILED.value,
            metadata_filters=_build_filters(entities),
            db_params=_build_db_params(entities),
            answer=_answer_stub(RouteType.UNSUPPORTED),
            sections=[],
            time_basis=_time_basis(entities),
            partial_answer=False,
        )

    sections: list[dict[str, Any]] = [
        {
            "type": "routing",
            "route_type": route.value,
            "confidence": result.confidence,
            "scores": result.scores,
            "used_retry": result.used_retry,
            "entities": entities.to_dict(),
        }
    ]

    return QuestionAnalysis(
        request_id=request_id,
        normalized_question=normalized,
        entities=entities,
        route_type=route,
        routing_confidence=result.confidence,
        routing_scores=result.scores,
        used_retry=result.used_retry,
        status=QueryStatus.SUCCESS,
        failure_reason=None,
        metadata_filters=_build_filters(entities),
        db_params=_build_db_params(entities),
        answer=_answer_stub(route),
        sections=sections,
        time_basis=_time_basis(entities),
        partial_answer=False,
    )
