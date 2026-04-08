# IRIS Graphio App - SDD

> Graphio App 개발을 위한 명세서
> 2025-03-01 기준

---

## 1. 기술 스택

### 1.1 필수 환경

| 항목      | 버전         | 비고             |
| --------- | ------------ | ---------------- |
| Python    | 3.11         | 필수             |
| LangGraph | v0.2.59 이상 | 필수             |
| LangChain | -            | LangGraph 의존성 |
| FastAPI   | -            | 웹 프레임워크    |

### 1.2 LLM

| 모델   | 설명                  |
| ------ | --------------------- |
| OpenAI | 기본 LLM (GPT 시리즈) |
| Ollama | 자체 모델 사용 시     |
| Gemma  | 자체 모델 사용 시     |

### 1.3 데이터베이스 / 스토리지

| 항목                  | 용도                                  |
| --------------------- | ------------------------------------- |
| PostgreSQL + pgvector | 벡터 검색, 문서 청킹 저장             |
| SQLite                | LangGraph 체크포인터 (대화 상태 유지) |
| MinIO                 | 파일 스토리지                         |
| FAISS                 | 벡터 스토어 (로컬)                    |

### 1.4 메시징 / 모니터링

| 항목     | 용도                 |
| -------- | -------------------- |
| RabbitMQ | 메시지 큐, Heartbeat |
| Phoenix  | 모니터링 (옵션)      |

### 1.5 환경 변수

```bash
# 필수
OPENAI_API_KEY=           # OpenAI API 키
APP_ID=                   # 애플리케이션 ID
LLM_MODEL=                # 사용할 LLM 모델

# PostgreSQL
C_DATABASE_HOST=
C_DATABASE_PORT=

# MinIO
C_MINIO_CLIENT_HOST=
C_MINIO_CLIENT_PORT=
```

---

## 2. 필수 규칙

### 2.1 필수 파일

| 파일명     | 설명                      |
| ---------- | ------------------------- |
| `agent.py` | AgentState 정의           |
| `graph.py` | LangGraph 워크플로우 정의 |

### 2.2 LangGraph 생성 이름

```python
# 반드시 이 이름으로 생성
graphio_app_flow = workflow.compile()
```

### 2.3 LLM 스트리밍 설정

```python
# 답변 생성용 (스트리밍 O)
LLM = ChatOpenAI(disable_streaming=False)

# 답변 생성 외 용도 (스트리밍 X) - 판단, 분류 등
LLM = ChatOpenAI(disable_streaming=True)
```

---

## 3. 프로젝트 구조

```
src/
├── api/              # API 레이어
├── services/         # 핵심 비즈니스 로직
├── service_utils/    # 서비스 유틸리티
├── utils/            # 공통 유틸리티
├── clients/          # 외부 API 클라이언트
├── core/             # 핵심 설정
└── db/               # 데이터베이스 연결
```

---

## 4. 소스 파일 명세

### 4.1 api/ - API 레이어

#### `graphio_app.py`

FastAPI 애플리케이션 진입점

| 엔드포인트                                       | 설명              |
| ------------------------------------------------ | ----------------- |
| `POST /graphio/graphio_app/v1/stream`            | SSE 스트리밍 응답 |
| `GET /graphio/graphio_app/v1/status`             | 상태 확인         |
| `GET /graphio/graphio_app/v1/download/{file_id}` | 파일 다운로드     |

라이프사이클 관리: Heartbeat 백그라운드 태스크, PID 파일 관리, Phoenix 연동, SQLite 체크포인터 초기화

#### `generator.py`

스트림 생성 로직

| 함수                          | 설명                                    |
| ----------------------------- | --------------------------------------- |
| `stream_generator()`          | LangGraph 이벤트를 SSE 형식으로 변환    |
| `add_message()`               | 대화 히스토리를 DB에 저장               |
| `langchain_to_chat_message()` | LangChain 메시지를 커스텀 형식으로 변환 |

커스텀 메시지 타입 처리: `editor`, `editor_start`, `editor_end`, `studio_url`, `studio_param`, `chart`, `file`, `loading`

#### `schema.py`

Pydantic 스키마 정의

| 모델          | 설명               |
| ------------- | ------------------ |
| `UserInput`   | 사용자 입력 모델   |
| `StreamInput` | 스트리밍 입력 모델 |
| `ChatMessage` | 채팅 메시지 모델   |

---

### 4.2 services/ - 핵심 비즈니스 로직

#### `graph.py` (필수)

LangGraph 워크플로우 정의

노드 구성:

- `ontology` - 온톨로지 정보 확인
- `ontology_config_info` - 온톨로지 설정 정보 로드
- `file_use` - 파일 사용 처리
- `model` - LLM 호출
- `tools` - 도구 실행
- `title` - 제목 생성
- `studio_agent`, `studio_url_agent`, `studio_param_agent` - Studio 보고서 처리
- `file_agent` - 파일 참조 처리
- `chart` - 차트 생성
- `clean_user_upload_files` - 파일 정리

#### `agent.py` (필수)

AgentState 정의

```python
class AgentState(MessagesState, total=False):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # 대화 메시지
    user_upload_files: Optional[list]      # 업로드된 파일 정보
    ontology_resource: Optional[list]      # 온톨로지 리소스
    studio_input: Optional[dict]           # Studio 입력
    studio_type: Optional[str]             # Studio 타입
    app_report_list: Optional[list]        # 앱 보고서 목록
```

#### `editor.py`

에디터 노드 처리

- 웹 검색 기반 콘텐츠 생성/수정
- 도구: `web_search` (DuckDuckGo)

#### `tools.py`

기본 도구 정의

| 도구                  | 설명               |
| --------------------- | ------------------ |
| `basic_question_tool` | 일반 질의응답 도구 |

#### `prompt.py`

프롬프트 템플릿 정의

---

### 4.3 service_utils/ - 서비스 유틸리티

#### `util_node.py`

공통 노드 함수

| 함수                     | 설명                    |
| ------------------------ | ----------------------- |
| `title_model()`          | 대화 제목 생성          |
| `ontology_info()`        | 온톨로지 정보 확인      |
| `ontology_config_info()` | 온톨로지 설정 정보 처리 |
| `file_use()`             | 파일 사용 노드          |

#### `file_use.py`

파일 관련 처리

| 함수                             | 설명                                                                     |
| -------------------------------- | ------------------------------------------------------------------------ |
| `get_top_similar_chunks()`       | pgvector 유사도 검색                                                     |
| `get_top_chunks_pgvector()`      | pgvector cosine 유사도 검색, 상대 임계값 기반 필터링 (최대 유사도 × 0.8) |
| `conversational_query_rewrite()` | 대화 기반 쿼리 재작성                                                    |
| `pending_file()`                 | 파일 사용 필요 여부 LLM 판단                                             |

#### `ontology.py`

온톨로지 연동

| 함수                          | 설명                          |
| ----------------------------- | ----------------------------- |
| `get_app_project_resource()`  | 프로젝트 리소스 조회          |
| `get_project_ontology_info()` | 온톨로지 정보 조회            |
| `get_elements()`              | Knowledge Graph에서 요소 조회 |

연동 API: Governance API, Knowledge Graph API

#### `studio_node.py`

Studio(보고서) 노드 처리

| 함수                   | 설명                       |
| ---------------------- | -------------------------- |
| `studio_agent()`       | 보고서 생성/조작 여부 판단 |
| `studio_url_agent()`   | 보고서 URL 생성            |
| `studio_param_agent()` | 보고서 파라미터 생성       |

보고서 타입: `generation` (생성), `operation` (조작)

#### `chart.py`

차트 생성 처리

| 함수                       | 설명                 |
| -------------------------- | -------------------- |
| `chart_agent()`            | 차트 생성 여부 판단  |
| `create_chart_rule_tool()` | Highcharts JSON 생성 |

지원 차트 타입: `area`, `line`, `column`, `pie`

#### `file_refer.py`

파일 참조 처리

| 함수                            | 설명                    |
| ------------------------------- | ----------------------- |
| `file_refer_agent()`            | 파일 다운로드 링크 생성 |
| `generate_minio_download_url()` | MinIO 다운로드 URL 생성 |

#### `title.py`

제목 생성 유틸리티

| 클래스         | 설명                  |
| -------------- | --------------------- |
| `TitleSummary` | 대화 제목 생성 클래스 |

---

### 4.4 utils/ - 공통 유틸리티

#### `models.py`

LLM 모델 팩토리

| 클래스             | 설명              |
| ------------------ | ----------------- |
| `ChatModelFactory` | 모델 생성 및 관리 |

지원 모델: OpenAI (GPT 시리즈), Ollama, Gemma

#### `store.py`

벡터 스토어 관리

| 클래스        | 설명                   |
| ------------- | ---------------------- |
| `VectorStore` | FAISS 기반 벡터 스토어 |

기능: 유사도 검색, 문서 추가/삭제, 로컬 저장/로드

#### `logger.py`

로깅 설정: 파일/콘솔 핸들러, 일별 롤링 (35일 보관)

#### `file_download.py`

파일 다운로드 처리

| 함수                  | 설명                |
| --------------------- | ------------------- |
| `save_temp_file()`    | 임시 파일 저장      |
| `resolve_by_id()`     | 파일 ID로 경로 조회 |
| `make_fileresponse()` | 파일 응답 생성      |

지원 형식: HWPX, PDF 등

#### `utils.py`

공통 유틸리티 함수

| 함수                          | 설명                    |
| ----------------------------- | ----------------------- |
| `pub_heartbeat()`             | RabbitMQ heartbeat 발행 |
| `start_phoenix()`             | Phoenix 연동            |
| `start_test_ui()`             | CORS 설정               |
| `find_latest_human_message()` | 최신 사용자 메시지 찾기 |

#### `minio_utils.py`, `minio_base.py`

MinIO 클라이언트: 파일 저장, 다운로드 URL 생성

#### `rabbitmq.py`

RabbitMQ 메시지 발행: 컨테이너 상태 메시지 전송

---

### 4.5 clients/ - 외부 API 클라이언트

#### `client.py`

| 클래스            | 설명                              |
| ----------------- | --------------------------------- |
| `AsyncHTTPClient` | httpx 기반 비동기 HTTP 클라이언트 |

연동 대상: App Platform API, Knowledge Graph API, Governance API

---

### 4.6 core/ - 핵심 설정

#### `config.py`

| 클래스   | 설명                             |
| -------- | -------------------------------- |
| `Config` | Pydantic Settings 기반 환경 설정 |

설정 항목:

- 일반: 호스트, 포트, 로그 레벨
- 스토리지, 모델 (LLM, Embedding)
- 온톨로지, App Platform, Knowledge Graph
- RabbitMQ, MinIO, DB, Phoenix
- Governance API, Rerank API

---

### 4.7 db/ - 데이터베이스

#### `connect_rdb.py`

PostgreSQL 연결 관리

| 클래스            | 설명                   |
| ----------------- | ---------------------- |
| `AsyncPostgresDB` | asyncpg 기반 커넥션 풀 |

| 메서드       | 설명           |
| ------------ | -------------- |
| `connect()`  | 커넥션 풀 생성 |
| `fetch()`    | 여러 행 조회   |
| `fetchrow()` | 단일 행 조회   |
| `close()`    | 커넥션 풀 종료 |

---

## 5. AgentState 정의

### 5.1 필수 필드

```python
from typing import Optional
from langgraph.graph import MessagesState
from service_utils.title import TitleOutput

class AgentState(MessagesState, total=False):
    title_output: TitleOutput                      # title node - 제목 생성
    user_upload_files: Optional[list]              # file_use node - 업로드 파일 내용 (DB 조회)
    user_upload_files_exclude: Optional[list]      # file_use node - 제외할 파일명
    files: Optional[list]                          # 파일 출처 정보
    ontology_resource: Optional[list]              # ontology node - ObjectType, ListType
```

### 5.2 선택 필드

```python
# Editor 노드 사용 시
editor_{name}_title: Optional[str]      # 에디터 탭 제목 설정

# Studio 노드 사용 시
studio_input: Optional[dict]            # studio agent node
studio_type: Optional[str]              # studio agent node
app_report_list: Optional[list]         # studio agent node
```

---

## 6. 공통 노드

### 6.1 노드 목록

| 노드명                    | 필수 | 설명                                                                                      |
| ------------------------- | :--: | ----------------------------------------------------------------------------------------- |
| `title`                   |  ✅  | 채팅 내용에 대한 제목 생성.`create_title` 설정에 따라 결정                                |
| `file_use`                |  ✅  | 파일 첨부 문서 처리. LLM이 DB 조회 필요 여부 판단 후 `state["user_upload_files"]`에 저장  |
| `clean_user_upload_files` |  ✅  | `user_upload_files`, `user_upload_files_exclude` 초기화. **`__end__` 직전에 반드시 추가** |
| `ontology`                |  ❌  | Graphio Portal 온톨로지 화면에 ObjectType 정보 활성화                                     |
| `chart`                   |  ❌  | 차트 요청 시 Highcharts JSON 생성                                                         |
| `editor`                  |  ❌  | 노드명에 "editor" 포함 시 editor 탭에 출력. 다중 editor 가능                              |
| `loader`                  |  ❌  | 로딩 UI 표시. **노드 내부에서 `loader()` 함수 호출 방식으로 사용** (별도 노드 불필요) |
| `studio`                  |  ❌  | IRIS VDAP Studio 보고서 연동                                                              |

### 6.2 file_use 노드 사용 예시

```python
def prepare_prompt(state: AgentState):
    full_instruction = instructions

    # file_use 노드 이후에만 접근 가능
    file_chunks = state.get("user_upload_files")
    if file_chunks:
        file_texts = [f"{i+1}. {chunk['document']}" for i, chunk in enumerate(file_chunks)]
        context = "\n".join(file_texts)
        full_instruction += (
            "\n\n다음은 사용자가 업로드한 자료의 중요한 내용입니다.\n"
            "해당 내용을 바탕으로 질문에 대해 친절하고 자연스럽게 설명해주세요:\n\n" + context
        )

    system_messages = [SystemMessage(content=full_instruction)]
    return system_messages + state["messages"]
```

### 6.3 loader 함수 사용 (로딩 메시지 처리)

#### 변경 사항

**기존 방식 (Deprecated)**
- 로딩 처리를 위해 별도의 LangGraph 노드를 생성하여 그래프에 연결하는 방식
- 예: `loader_temp` 노드를 생성하고 그래프에 추가하여 사용

**현재 방식 (권장)**
- 노드 내부의 원하는 시점에서 `loader()` 함수를 직접 호출하여 로딩 메시지를 즉시 응답
- 별도의 노드를 생성할 필요 없이, 각 노드 함수 내에서 필요한 시점에 호출 가능
- 하나의 노드 내에서 여러 번 `loader()` 호출 가능

#### 사용 방법

```python
from utils.loading import loader

async def temp(state: AgentState, config: RunnableConfig):
    # 노드 실행 시작 시점에 로딩 메시지 전송
    await loader("목차를 생성 중입니다.", config=config)
    
    # 실제 작업 수행
    # ... 작업 로직 ...
    
    # 다른 작업 시작 시점에 또 다른 로딩 메시지 전송 가능
    await loader("문서를 분석 중입니다.", config=config)
    
    # ... 추가 작업 로직 ...
    
    return {"messages": [...]}
```

#### 실제 사용 예시

**graph.py의 acall_model 노드**
```python
async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    try:
        await loader("model 노드 실행중입니다.", config)
        model_runnable = wrap_model(chat_model)
        response = await model_runnable.ainvoke(state, config)
        # ... 나머지 로직 ...
```

**graph.py의 pending_title 노드**
```python
async def pending_title(state: AgentState, config: RunnableConfig) -> Literal["title", "done"]:
    create_title = config["metadata"]["create_title"]
    if create_title:
        await loader("제목 생성 중입니다.", config)
        return "title"
    return "done"
```

#### 구현 세부사항

- `loader()` 함수는 `utils.loading` 모듈에 정의되어 있음
- 내부적으로 `adispatch_custom_event`를 사용하여 커스텀 이벤트로 로딩 메시지 전송
- `config` 파라미터는 필수 (커스텀 이벤트 전송을 위해 필요)
- 로딩 메시지는 `{"type": "loading"}` 타입으로 클라이언트에 전달됨
- 로딩 종료는 별도로 처리하지 않아도 됨 (다음 메시지가 오면 자동으로 대체됨)

#### 주의사항

- `loader()` 함수는 `async` 함수이므로 `await` 키워드와 함께 사용해야 함
- `config` 파라미터를 반드시 전달해야 함 (없으면 로딩 메시지가 전송되지 않음)
- 노드 함수의 시그니처에 `config: RunnableConfig` 파라미터가 포함되어 있어야 함

---

## 7. 워크플로우 순서

```
ontology
    ↓
ontology_config_info
    ↓
pending_file ─────→ file_use (필요 시)
    ↓                   ↓
    └───────────────────┘
    ↓
model (LLM 호출)
    ↓
pending_tool_calls ──→ tools → model (반복)
    ↓                      ↓
    └──────────────────────┘
    ↓
studio_agent ─→ studio_url_agent / studio_param_agent
    ↓
file_agent
    ↓
chart
    ↓
pending_title ──→ title (필요 시)
    ↓                ↓
    └────────────────┘
    ↓
clean_user_upload_files
    ↓
END
```

**규칙**: 개발한 노드는 `ontology`와 `title` 사이에 위치

---

## 8. API 응답 형식

### 8.1 기본 형식

SSE 형식으로 실시간 스트리밍 응답 전송. 각 메시지는 `data: ` 접두사와 JSON 형식.

```
data: {"type": "token", "content": "텍스트"}
```

### 8.2 메시지 타입

#### 기본 타입

| type            | 설명                                        |
| --------------- | ------------------------------------------- |
| `token`         | 일반 LLM 응답 토큰                          |
| `title_token`   | 제목 생성 토큰                              |
| `message`       | 완전한 메시지 객체 (비스트리밍 모드)        |
| `message_title` | 제목 메시지                                 |
| `done`          | 완료.`{"type": "done", "thread_id": "xxx"}` |
| `cancelled`     | 클라이언트 연결 끊김 시                     |

#### 에디터 타입

| type           | 설명                        |
| -------------- | --------------------------- |
| `editor_start` | 에디터 시작, content에 제목 |
| `editor`       | 에디터 콘텐츠 토큰          |
| `editor_end`   | 에디터 종료                 |

#### 차트/파일 타입

| type    | content 형식                                      |
| ------- | ------------------------------------------------- |
| `chart` | Highcharts JSON 문자열                            |
| `file`  | `[{"title":"파일명.pdf","url":"/download/경로"}]` |

#### Studio 타입

| type                 | 설명                  |
| -------------------- | --------------------- |
| `studio_url_start`   | URL 생성 시작         |
| `studio_url`         | 생성된 URL            |
| `studio_url_end`     | `{"isSuccess": true}` |
| `studio_param_start` | 파라미터 생성 시작    |
| `studio_param`       | 생성된 파라미터       |
| `studio_param_end`   | `{"isSuccess": true}` |

#### 로딩 타입

| type          | 설명                                                                    |
| ------------- | ----------------------------------------------------------------------- |
| `loading`     | 로딩 시작. 노드 내부에서 `loader()` 함수 호출 시 자동으로 전송됨        |
| `loading_end` | 로딩 종료 (현재는 자동 처리되므로 명시적 호출 불필요)                   |
| `highlights`  | 하이라이트 메시지                                                       |

**로딩 메시지 전송 방식:**
- 노드 함수 내에서 `await loader("메시지 내용", config=config)` 호출 시
- `{"type": "loading", "content": "메시지 내용"}` 형식으로 클라이언트에 전송됨
- 여러 번 호출 가능하며, 새로운 로딩 메시지가 오면 이전 메시지를 대체함

### 8.3 응답 예시

```
data: {"type": "loading", "content": ""}
data: {"type": "token", "content": "모비젠은"}
data: {"type": "token", "content": "한국의"}
data: {"type": "token", "content": "AI 기업입니다."}
data: {"type": "chart", "content": "{\"chart\":{\"type\":\"column\"},\"title\":{\"text\":\"매출\"},...}"}
data: {"type": "file", "content": "[{\"title\":\"보고서.pdf\",\"url\":\"/download/abc123\"}]"}
data: {"type": "done", "thread_id": "247c6285-8fc9-4560-a83f-4e6285809254"}
```

### 8.4 처리 규칙

#### 스트리밍 모드 (`stream_tokens: true`)

- 토큰 단위로 `token` 타입 전송
- 커스텀 타입(`chart`, `file` 등)은 즉시 전송

#### 비스트리밍 모드 (`stream_tokens: false`)

- 완전한 `message` 객체로 전송
- 개발 모드(`MODE=dev`)에서도 비스트리밍

#### 에디터 노드 처리 순서

```
editor_start (제목) → editor (토큰 반복) → editor_end
```

#### Studio 보고서 처리 순서

```
studio_url_start → studio_url → studio_url_end
studio_param_start → studio_param → studio_param_end
```

---

## 9. 스트리밍 요청 예시

```http
POST /graphio/graphio_app/v1/stream
Content-Type: application/json
Cookie: access_token=xxx

{
  "message": "모비젠에 대해 알려줘",
  "model": "gpt-4o",
  "thread_id": "247c6285-8fc9-4560-a83f-4e6285809254",
  "thread_history": true,
  "stream_tokens": true,
  "file_names": [],
  "this_file": []
}
```

응답 헤더:

```
Content-Type: text/event-stream
Cache-Control: no-cache, no-store, must-revalidate
Connection: keep-alive
```
