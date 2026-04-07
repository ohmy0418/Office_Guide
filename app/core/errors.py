from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorResponseBody(BaseModel):
    """API 공통 에러 응답 뼈대 — 세부 필드는 Phase 이후 확정."""

    error_code: str = Field(..., description="시스템/추적용 코드 (docs/specify.md error_code)")
    message: str
    detail: str | None = None


def http_error(
    *,
    status_code: int,
    error_code: str,
    message: str,
    detail: str | None = None,
) -> HTTPException:
    body = ErrorResponseBody(error_code=error_code, message=message, detail=detail).model_dump(
        exclude_none=True
    )
    return HTTPException(status_code=status_code, detail=body)


def not_found(message: str = "리소스를 찾을 수 없습니다.") -> HTTPException:
    return http_error(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code="NOT_FOUND",
        message=message,
    )
