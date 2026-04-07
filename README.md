# Office_Guide

회사생활가이드 v1 백엔드 저장소. 기준 문서는 `docs/specify.md`, 작업 순서는 `docs/plan.md`이다.

## 요구 사항

- Python 3.11+
- PostgreSQL 16 + pgvector (로컬은 `docker-compose` 권장)

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

- API 문서: <http://127.0.0.1:8000/docs>
- 헬스: `GET /api/v1/health`

## 테스트

```bash
pytest
```

## 임베딩 차원

Alembic 초기 마이그레이션의 벡터 차원(기본 1536)과 `EMBEDDING_DIMENSION` 환경 변수는 반드시 맞출 것.
