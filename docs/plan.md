# 회사생활가이드 v1 개발 계획서 (plan.md)

## 1. 문서 목적
이 문서는 회사생활가이드 v1 통합 명세서를 기준으로, 실제 개발 작업 순서와 산출물을 정의한 실행 계획 문서다.
개발 범위를 단계별로 나누고, 각 단계에서 구현할 항목, 선행 조건, 완료 기준을 명시한다.

---

## 2. 개발 기준선

본 계획은 아래 기준을 전제로 한다.

- 정형 조회는 사전 정의 SQL 또는 API 중심으로 시작한다.
- 문서 검색은 하이브리드 검색(키워드 검색 + 유사도 검색)을 기본으로 한다.
- 결과 결합 기본값은 RRF를 사용한다.
- 혼합 조회는 기본적으로 병렬 처리하되, 의존 관계가 명확한 경우에만 순차 처리한다.
- PDF 수정 반영은 전체 재색인을 기본으로 한다.
- 운영 로그와 품질 평가 로그는 분리 저장한다.
- 검색 기준선은 문서 후보 top 3, chunk 후보 top 10, rerank 6, 최종 context 4를 기본으로 한다.

---

## 3. 기술 스택

본 시스템은 문서 수집, 파싱, 검색, 응답 생성, 운영 기능을 안정적으로 구현하기 위해 아래 기술 스택을 기준으로 개발한다.

| 영역 | 기준 스택 | 역할 |
| --- | --- | --- |
| 개발 언어 | Python 3.11 | 백엔드 및 파이프라인 구현 |
| 앱 로직 / RAG 구성 | LangChain | 프롬프트 구성, retriever 연결, 문서 체인, LLM 호출 |
| 워크플로 제어 | LangGraph | 상태 관리, 분기 처리, 실패 응답 제어 |
| 운영 DB | PostgreSQL | 문서 메타데이터, 운영 로그, 평가 데이터 저장 |
| 벡터 검색 | pgvector | 임베딩 벡터 저장 및 유사도 검색 |
| 답변 생성 모델 | OpenAI | 검색/조회 결과 기반 답변 생성 |
| 백엔드 API | FastAPI | 사용자 및 운영 API 제공 |
| 파일 저장소 | MinIO(AIStor) 또는 사내 파일 서버 | 원본 파일 저장 |
| PDF 파싱 | PyMuPDF | 텍스트/표/구조 추출 |
| 구조 보강 | PyMuPDF4LLM | 제목/소제목 추출, 구조 복원 |
| OCR | OCRmyPDF | 스캔 PDF 텍스트 레이어 추가 |
| 임베딩 모델 | text-embedding-3-small 우선 | chunk 임베딩 생성 |

### 기술 스택 적용 원칙
- 백엔드와 파이프라인은 Python 3.11 기준으로 통일한다.
- RAG 흐름은 LangChain 기반으로 구성하고, 상태 제어는 LangGraph로 분리한다.
- 운영 데이터와 검색 데이터는 PostgreSQL + pgvector 조합으로 관리한다.
- 원본 파일은 MinIO 또는 사내 파일 서버에 저장한다.
- PDF 파싱은 PyMuPDF 계열을 기본으로 하고, 스캔 문서는 OCRmyPDF를 보조적으로 사용한다.

---

## 4. 선행 결정 필요 항목

아래 항목은 본격 구현 전에 우선 확정하거나, 최소한 임시 기준을 정해야 한다.

1. 운영 기능 권한을 `관리자만`으로 둘지, `권한 있는 내부 사용자`로 둘지 확정
2. chunk 검색 기본 전략을 `병렬 검색`으로 확정할지 여부
3. 실패 시 `실패 사유 안내만 제공`할지, `재처리 기능까지 포함`할지 여부
4. route_type / status / document_status / failure_reason / error_code enum 표준 확정

---

## 5. 전체 개발 단계

- Phase 0. 기준선 확정 및 작업 준비
- Phase 1. 프로젝트 베이스 및 저장 구조 구축
- Phase 2. 문서 수집 및 인덱싱 파이프라인 구현
- Phase 3. 질문 분석 및 라우팅 구현
- Phase 4. 문서 검색(RAG) 구현
- Phase 5. 정형 조회 및 혼합 조회 구현
- Phase 6. 답변 생성, fallback, 로그 구현
- Phase 7. 운영 기능 및 관리자 API 구현
- Phase 8. 품질 평가 체계 구축
- Phase 9. 통합 테스트 및 v1 릴리스 준비

---

## 6. 단계별 상세 계획

### Phase 0. 기준선 확정 및 작업 준비

#### 목표
개발 중 흔들릴 수 있는 주요 기준선을 먼저 잠그고, 팀이 같은 기준으로 구현할 수 있게 한다.

#### 작업 항목
- v1 검색 기준선 확정
  - 문서 후보 top 3
  - chunk 후보 top 10
  - rerank 6
  - context 4
- 결과 결합 기본값을 RRF로 확정
- chunk 검색 기본 전략을 병렬 검색으로 잠정 확정
- 운영 기능 역할을 `관리자` 또는 `권한 있는 내부 사용자` 중 하나로 확정
- route_type / status / document_status / failure_reason / error_code enum 초안 작성
- API 응답 공통 포맷 초안 작성

#### 공통 enum 정의
- route_type / status / document_status / failure_reason / error_code enum 표준 확정
- 확정된 enum을 API 응답, 운영 로그, 문서 상태값에 반영

#### 산출물
- 기준선 결정 회의록
- enum 초안
- API 응답 공통 규약 초안

#### 완료 기준
- 구현팀이 논의 없이 바로 사용할 수 있는 기준값이 문서로 남아 있어야 한다.

---

### Phase 1. 프로젝트 베이스 및 저장 구조 구축

#### 목표
백엔드 프로젝트 구조, DB 스키마, 저장소 연동, 기본 개발 환경을 준비한다.

#### 작업 항목
- FastAPI 프로젝트 초기 구성
- LangChain / LangGraph 기본 구조 연결
- PostgreSQL 및 pgvector 연결
- 파일 스토리지(MinIO 또는 사내 파일 서버) 연동
- DB 스키마 생성
  - documents
  - document_chunks
  - query_logs
  - retrieval_eval_logs
- 공통 상태값(enum) 정의
- 공통 에러 응답 구조 정의

#### 산출물
- 프로젝트 초기 코드베이스
- DB migration 초안
- 환경설정 샘플 파일
- 스토리지 연동 설정

#### 완료 기준
- 문서 메타데이터를 DB에 저장할 수 있어야 한다.
- 원본 파일을 스토리지에 업로드할 수 있어야 한다.
- 로컬/개발 환경에서 서버가 정상 실행되어야 한다.

---

### Phase 2. 문서 수집 및 인덱싱 파이프라인 구현

#### 목표
문서 업로드 후 검색 가능한 데이터로 반영되는 전체 ingestion 파이프라인을 구현한다.

#### 작업 항목
- 문서 업로드 처리
- 메타데이터 등록 및 상태 초기화
- PDF 변환/정규화 처리
- OCR 분기 처리
- PDF 파싱
  - 본문
  - 표
  - 제목/소제목
  - 문단 구조
  - 페이지 정보
- 정제/정규화 처리
- 의미 기반 chunk 분할 구현
- chunk 임베딩 생성
- documents / document_chunks 저장
- 문서 상태 업데이트
  - pending
  - processing
  - completed
  - failed
  - reindex_required

#### 세부 구현 순서
1. upload → documents 등록
2. status = pending
3. ingest 시작 시 status = processing
4. PDF 변환/정규화
5. OCR 필요 여부 판별
6. 파싱 및 정제
7. chunk 분할
8. embedding 생성
9. 저장
10. completed 또는 failed 갱신

#### 산출물
- ingestion 서비스 모듈
- 상태 전이 로직
- 실패 사유 기록 구조

#### 완료 기준
- 문서 1건 업로드 후, `documents`와 `document_chunks`에 연결된 데이터가 저장되어야 한다.
- 실패 시 `error_code`, `error_message`, `status`, `failure_reason`가 기록되어야 한다.

---

### Phase 3. 질문 분석 및 라우팅 구현

#### 목표
사용자 질문을 문서형/정형 조회형/혼합 조회형/처리 불가로 분류하고, 후속 파라미터를 생성한다.

#### 작업 항목
- 최소 핵심 정보 추출 구현
  - 사람 이름
  - 부서명
  - 규정명/문서명
  - 시점 표현
  - 조건값
- 사전/동의어 정규화 초안 적용
- route_type 분류 로직 구현
- 규칙 기반 라우팅 우선 구현
- 필요 시 LLM 보조 분류 훅 설계
- 미시도 route 최대 1회 재시도 로직 구현
- 처리 불가 질문 fallback 전환 구현

#### 산출물
- question analyzer 모듈
- route_type 분류기
- query normalization 모듈

#### 완료 기준
- 질문 1건이 하나의 주 처리 유형으로만 분류되어야 한다.
- 추출 결과가 검색 필터 또는 DB/API 파라미터 생성에 활용 가능해야 한다.

---

### Phase 4. 문서 검색(RAG) 구현

#### 목표
Pre-Retrieval → Retrieval → Post-Retrieval 구조의 문서 검색 파이프라인을 구현한다.

#### 작업 항목
#### Pre-Retrieval
- 질문 정규화/질의 재작성
- 하위 쿼리 분해
- 키워드 검색 질의 생성
- 의미 기반 검색 질의 생성
- 메타데이터 필터 생성

#### Retrieval
- PostgreSQL FTS 기반 키워드 검색 구현
- pgvector 기반 유사도 검색 구현
- 문서 후보 검색 구현
- chunk 후보 검색 구현
- 병렬 검색 orchestration 구현
- RRF 결합 구현

#### Post-Retrieval
- 후보군 중복 제거
- 1차 점수화
- rerank 적용
- context 편집
  - 반복 chunk 제거
  - 긴 chunk 압축
  - 출처 정보 유지

#### 산출물
- RAG pipeline 모듈
- retriever 구현
- RRF 결합기
- context builder

#### 완료 기준
- 문서형 질문에 대해 문서명, 조항/제목, 페이지를 포함하는 context를 생성할 수 있어야 한다.
- 기본 기준선(top3/top10/rerank6/context4)이 코드 상에서 설정 가능해야 한다.

---

### Phase 5. 정형 조회 및 혼합 조회 구현

#### 목표
정형 조회형 질문과 혼합 조회형 질문을 안정적으로 처리한다.

#### 작업 항목
#### 정형 조회
- 사전 정의 SQL 구현
- 내부 API 조회 모듈 구현
- 지원 범위 구현
  - 이름 검색
  - 유사 이름 검색
  - 부서 검색
  - 조직 구조 조회
  - 연락처/이메일 조회
  - 담당자/담당 부서 조회

#### 혼합 조회
- 질문 분해 구현
- 문서 조회 파트 실행
- 정형 조회 파트 실행
- 병렬 fan-out 및 결과 merge 구현
- 의존 관계 질문의 순차 실행 처리
- 문서 기준일/정형 조회 시점 병합 표시
- sections / time_basis / failure_reason 구조 구현

#### 산출물
- structured lookup 모듈
- hybrid orchestrator
- merge formatter

#### 완료 기준
- 혼합 조회 질문에 대해 `기준/절차`와 `현재 담당 정보`를 구분한 응답 구성이 가능해야 한다.
- 한쪽 결과만 있어도 부분 답변이 가능해야 한다.

---

### Phase 6. 답변 생성, fallback, 로그 구현

#### 목표
검색/조회 결과를 최종 답변으로 변환하고, 실패 시 안전한 fallback과 로그 저장을 처리한다.

#### 작업 항목
- 문서형 답변 포맷 구현
- 정형 조회형 답변 포맷 구현
- 혼합 조회형 답변 포맷 구현
- 출처 / 링크 / 최신성 표시 구현
- partial_answer 구조 구현
- fallback 응답 템플릿 구현
- 예외 처리 분기 구현
- 운영 로그 저장 구현
  - request_id
  - user_id
  - question
  - route_type
  - status
  - latency_ms
  - error_code
  - error_message
  - failure_reason
- 품질 평가 로그 저장 구조 구현

#### 산출물
- answer builder
- fallback handler
- logging middleware / service

#### 완료 기준
- 질문 처리 성공/실패/fallback가 모두 로그에 기록되어야 한다.
- 근거 없는 확정형 답변 없이 fallback 전환이 가능해야 한다.

---

### Phase 7. 운영 기능 및 관리자 API 구현

#### 목표
문서 업로드와 반영 상태 확인을 운영할 수 있는 최소 기능을 제공한다.

#### 작업 항목
- 문서 업로드 API 구현
- 문서 반영 요청 API 구현
- 반영 상태 조회 API 구현
- 실패 사유 조회 구현
- 운영 기능 권한 검증 구현
- 업로드/반영 상태 확인용 최소 화면 또는 내부 테스트 도구 구현

#### API 범위
- `POST /api/v1/documents/upload`
- `POST /api/v1/documents/{document_id}/ingest`
- `GET /api/v1/documents/{document_id}/status`

#### 산출물
- 관리자 API
- 운영 테스트 화면 또는 운영용 요청 스크립트

#### 완료 기준
- 문서 업로드 후 상태를 조회할 수 있어야 한다.
- 실패 상태에서 오류 코드와 메시지, 실패 원인을 확인할 수 있어야 한다.

---

### Phase 8. 품질 평가 체계 구축

#### 목표
검색 품질을 측정하고 실험 가능한 최소 체계를 만든다.

#### 작업 항목
- 평가셋 수집
- 정답 문서 / 정답 chunk 라벨링
- Recall@1 / Recall@3 / Recall@5 계산 스크립트 구현
- 비교 실험 구조 구현
  - BM25/FTS 단독
  - 벡터 단독
  - 하이브리드
  - RRF 적용 전후
  - rerank 적용 전후
  - 메타데이터 필터 적용 전후

#### 산출물
- evaluation dataset
- evaluation runner
- 비교 결과 보고서 템플릿

#### 완료 기준
- 최소 100개 이상 질문으로 Recall 지표 산출이 가능해야 한다.
- 설정 조합별 비교 결과를 확인할 수 있어야 한다.

---

### Phase 9. 통합 테스트 및 v1 릴리스 준비

#### 목표
전체 흐름을 종단간으로 검증하고, v1 릴리스 가능 상태를 만든다.

#### 작업 항목
- 문서 업로드 → 인덱싱 → 검색 → 답변까지 E2E 테스트
- 문서형 / 정형 조회형 / 혼합 조회형 시나리오 테스트
- fallback 시나리오 테스트
- 운영 기능 관리자 권한 테스트
- API 응답 스키마 검증
- 로그 누락 여부 확인
- 성능 점검
  - top3/top10/rerank6/context4 기준 동작 확인
  - latency 측정
- 릴리스 체크리스트 작성

#### 산출물
- E2E 테스트 시나리오
- QA 체크리스트
- 릴리스 노트 초안

#### 완료 기준
- 핵심 시나리오가 모두 정상 동작해야 한다.
- fallback, 운영 기능 관리자 권한 검증, 로그 기록이 누락 없이 동작해야 한다.
- v1 릴리스 범위 내 기능이 문서와 실제 구현에서 일치해야 한다.

---

## 7. 병행 관리할 이슈 목록

개발 중 병행해서 확인해야 할 이슈는 아래와 같다.

1. 관리자 vs 권한 있는 내부 사용자 역할 체계 최종 확정
2. 실패 사유 안내만 제공할지, 재처리 기능까지 포함할지 결정
3. 사전/동의어 사전 운영 주체와 반영 방식 확정
4. chunk 검색 전략 병렬/순차 비교 결과 검토

---

## 8. 우선순위 요약

### Must
- 프로젝트 베이스 구축
- DB/스토리지 구축
- 문서 ingestion 구현
- 라우팅 구현
- RAG 구현
- 정형 조회 구현
- 혼합 조회 구현
- 답변 생성 및 fallback 구현
- 로그 구현
- 운영 API 구현

### Should
- 최소 운영 도구
- 품질 평가 체계
- 평가셋 구축
- rerank 튜닝

### Later
- Text-to-SQL 제한적 도입 검토
- 가중합 랭킹 도입 검토
- PDF 증분 색인 검토
- 관리자 UI 고도화
