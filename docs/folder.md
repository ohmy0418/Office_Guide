### (1차) 프로젝트 아키텍처

```
office_guide/                    # 프로젝트 루트(이름은 팀 컨벤션에 맞게)
├── pyproject.toml               # 또는 requirements.txt
├── README.md
├── .env.example
├── docker-compose.yml           # 선택: app + postgres (+ minio)
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱 생성, 라우터 마운트
│   ├── config.py                # 설정(Pydantic Settings)
│   ├── dependencies.py          # DB 세션, 공통 DI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # v1 라우터 집계
│   │       └── health.py        # /health 등
│   ├── core/
│   │   ├── __init__.py
│   │   ├── enums.py             # route_type, status, document_status, failure_reason
│   │   └── errors.py            # 공통 에러 바디/HTTPException 헬퍼
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py              # declarative Base
│   │   ├── session.py           # engine, SessionLocal
│   │   └── models/              # SQLAlchemy 모델 (테이블 4종)
│   │       ├── document.py
│   │       ├── document_chunk.py
│   │       ├── query_log.py
│   │       └── retrieval_eval_log.py
│   ├── schemas/                 # Pydantic 요청/응답 (Phase 1: 최소만)
│   │   └── common.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── storage.py           # 스토리지 업로드/경로 생성
│   └── pipelines/               # LangChain / LangGraph 확장용 (Phase 1: 패키지만)
│       ├── __init__.py
│       └── placeholder.py
└── tests/
    ├── __init__.py
    └── test_health.py
```

## 생성·갱신된 구성
- 프로젝트: pyproject.toml(setuptools 빌드, app 패키지), .gitignore, .env.example, README.md 실행 안내
- 인프라: docker-compose.yml — pgvector/pgvector:pg16
- Alembic: alembic.ini, alembic/env.py, alembic/script.py.mako, alembic/versions/0001_initial_schema.py
- documents, document_chunks(pgvector Vector(1536)), query_logs, retrieval_eval_logs(request_id PK, JSONB 필드)
- 앱: app/main.py, app/config.py, app/dependencies.py
- API v1: GET /api/v1/health
- DB: app/db/session.py, app/db/models/* — 명세 9절 컬럼에 맞춘 SQLAlchemy 2.0 모델
- 공통: app/core/enums.py, app/core/errors.py, app/schemas/common.py(헬스용 최소 스키마)
- 스토리지: app/services/storage.py — 로컬 디렉터리 저장(이후 MinIO 등으로 교체 가능)
- 자리만: app/pipelines/placeholder.py
- 테스트: tests/test_health.py — 로컬에서 pytest 통과 확인함

### 설명
- GET /api/v1/health: 서버가 떠 있고 라우팅이 정상인지 확인하는 헬스(상태) 엔드포인트
