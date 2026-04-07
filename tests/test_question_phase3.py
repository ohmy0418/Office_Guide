from app.core.enums import RouteType
from app.services.question.analyze import analyze_question
from app.services.question.extraction import extract_entities
from app.services.question.normalize import normalize_question
from app.services.question.rules_router import classify_route


def test_normalize_synonym() -> None:
    assert "법인카드" in normalize_question("법카 한도가 어떻게 돼?")


def test_extract_email() -> None:
    e = extract_entities("홍길동 이메일은 hong@example.com 야")
    assert "hong@example.com" in e.emails


def test_classify_rag() -> None:
    e = extract_entities("연차 신청 절차와 규정을 알려줘")
    r = classify_route("연차 신청 절차와 규정을 알려줘", e)
    assert r.route_type == RouteType.RAG


def test_classify_db_api() -> None:
    q = "피플팀 담당자 이메일이 뭐야?"
    e = extract_entities(q)
    r = classify_route(q, e)
    assert r.route_type == RouteType.DB_API


def test_analyze_hybrid_signal() -> None:
    q = "기숙사 신청 규정과 담당 부서 연락처를 알려줘"
    a = analyze_question(q)
    assert a.route_type in (RouteType.HYBRID, RouteType.RAG, RouteType.DB_API)
