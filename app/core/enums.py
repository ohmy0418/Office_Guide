from enum import StrEnum


class RouteType(StrEnum):
    RAG = "rag"
    DB_API = "db_api"
    HYBRID = "hybrid"
    UNSUPPORTED = "unsupported"


class QueryStatus(StrEnum):
    SUCCESS = "success"
    FALLBACK = "fallback"
    ERROR = "error"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REINDEX_REQUIRED = "reindex_required"


class FailureReason(StrEnum):
    ROUTING_FAILED = "routing_failed"
    NO_RESULT = "no_result"
    PERMISSION_DENIED = "permission_denied"
    PARSE_FAILED = "parse_failed"
    OCR_FAILED = "ocr_failed"
    EMBEDDING_FAILED = "embedding_failed"
    UNKNOWN = "unknown"


class ErrorCode(StrEnum):
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ROUTING_FAILED = "ROUTING_FAILED"
    NO_RESULT = "NO_RESULT"
    PARSE_FAILED = "PARSE_FAILED"
    OCR_FAILED = "OCR_FAILED"
    EMBEDDING_FAILED = "EMBEDDING_FAILED"
    INDEX_SAVE_FAILED = "INDEX_SAVE_FAILED"
    DB_QUERY_FAILED = "DB_QUERY_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
