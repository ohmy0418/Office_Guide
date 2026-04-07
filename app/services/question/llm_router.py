from __future__ import annotations

"""
LLM 보조 분류 훅 (Phase 3 자리).
OPENAI_API_KEY가 있을 때만 선택적으로 호출할 수 있게 확장한다.
현재는 규칙 기반 결과를 그대로 신뢰한다.
"""

from app.config import settings
from app.core.enums import RouteType
from app.services.question.extraction import ExtractedEntities


def maybe_refine_route(
    question: str,
    entities: ExtractedEntities,
    preliminary: RouteType,
) -> RouteType | None:
    """LLM으로 보정할 경우 RouteType을 반환, 스킵 시 None."""
    if not settings.OPENAI_API_KEY:
        return None
    # [확인 필요] 프롬프트·모델·비용 한도 확정 후 구현
    return None
