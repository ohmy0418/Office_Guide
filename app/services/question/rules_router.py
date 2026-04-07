from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.enums import RouteType
from app.services.question.extraction import ExtractedEntities


@dataclass
class RoutingResult:
    route_type: RouteType
    confidence: float
    scores: dict[str, float]
    used_retry: bool


_RAG_KEYWORDS = (
    "규정",
    "가이드",
    "매뉴얼",
    "절차",
    "신청",
    "기준",
    "방침",
    "정책",
    "어떻게",
    "가능",
    "필요",
    "조건",
    "승인",
)
_DB_KEYWORDS = (
    "이메일",
    "전화",
    "연락처",
    "사번",
    "담당자",
    "누구",
    "소속",
    "조직도",
    "직통",
    "내선",
    "휴대폰",
    "핸드폰",
)


def _score_doc(text: str, entities: ExtractedEntities) -> float:
    s = 0.0
    for k in _RAG_KEYWORDS:
        if k in text:
            s += 1.2
    if entities.document_hints:
        s += 2.5
    if re.search(r"(?:신청|제출|승인|절차|방법)", text):
        s += 1.0
    return s


def _score_struct(text: str, entities: ExtractedEntities) -> float:
    s = 0.0
    for k in _DB_KEYWORDS:
        if k in text:
            s += 1.1
    if entities.emails:
        s += 3.0
    if entities.phones:
        s += 2.0
    if entities.person_names:
        s += 1.5
    if entities.departments and any(x in text for x in ("어디", "누구", "찾", "알려")):
        s += 1.2
    return s


def _compute_scores(text: str, entities: ExtractedEntities) -> dict[str, float]:
    rag = _score_doc(text, entities)
    db = _score_struct(text, entities)
    hybrid = 0.0
    if rag >= 1.2 and db >= 1.2:
        hybrid = rag * 0.55 + db * 0.55 + 0.8
    else:
        hybrid = min(rag, db) * 0.35
    return {
        RouteType.RAG.value: rag,
        RouteType.DB_API.value: db,
        RouteType.HYBRID.value: hybrid,
    }


def classify_route(
    text: str,
    entities: ExtractedEntities,
    *,
    min_confidence: float = 1.8,
    retry_floor: float = 1.05,
) -> RoutingResult:
    """
    규칙 기반 route_type 1건.
    1차 판정이 기준 미만이면, 서로 다른 상위 후보를 1회 재평가(미시도 경로 탐색).
    """
    scores = _compute_scores(text, entities)
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_name, best_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0.0

    used_retry = False

    if best_score >= min_confidence:
        return RoutingResult(RouteType(best_name), best_score, scores, used_retry)

    # 재시도: 문서·정형 신호가 동시에 있으면 hybrid 우선
    if scores[RouteType.RAG.value] >= retry_floor and scores[RouteType.DB_API.value] >= retry_floor:
        used_retry = True
        hy = scores[RouteType.HYBRID.value]
        return RoutingResult(RouteType.HYBRID, max(hy, best_score, second_score), scores, used_retry)

    # 재시도: 2순위 채택
    if second_score >= retry_floor:
        used_retry = True
        second_name = ordered[1][0]
        return RoutingResult(RouteType(second_name), second_score, scores, used_retry)

    # 최후: 최고점이라도 일정 이상이면 채택
    if best_score >= retry_floor:
        used_retry = True
        return RoutingResult(RouteType(best_name), best_score, scores, used_retry)

    return RoutingResult(RouteType.UNSUPPORTED, best_score, scores, used_retry)
