## 1. 핵심 개발 원칙

**1. 프로젝트 명칭**

- Graphio App 프로젝트

## **2. 핵심 개발 원칙**

### 2.1 품질/정확성 보장

- 타입 시스템을 활용하여 런타임 오류를 사전에 방지한다
- 사용자 입력은 검증 후 처리한다

### 2.2 성능/부하 관리

- 대상 시스템에 과도한 부하를 주지 않도록 적절한 조치를 취한다
- API 호출 시 타임아웃을 설정한다

### 2.3 테스트 원칙

- **모든 기능은 테스트 코드가 있어야 한다**

### 2.4 안정성/복원력

- 외부 시스템 호출 실패 시 재시도 로직을 구현한다
- 에러 발생 시 사용자에게 명확한 메시지를 표시한다

### 2.5 보안/권한

- 민감 정보는 로그에 출력하지 않는다
- 모든 외부 입력은 검증한다
- **개인정보 데이터는 화면에 표시 시 마스킹 처리한다**

### 2.6 관찰성/유지보수성

- 각 처리 단계마다 적절한 로그를 출력한다
- 에러 발생 시 추적 가능한 정보를 포함한다
- 함수와 클래스에 목적을 설명하는 주석을 작성한다
- **한 함수는 한 가지 기능만 수행한다**
- **재사용 가능한 로직은 공통 함수로 분리한다**
- **함수의 책임이 명확해야 하며, 이름만으로도 기능을 이해할 수 있어야 한다**

### 2.7 에러 처리 규칙

**Response 형식 통일:**

- 모든 API 응답은 통일된 구조를 사용한다
- Backend (BE)는 외부 Backend Services 응답을 받아 통일된 형식으로 변환한다
- 성공 응답:

<pre class="code-block" data-language="json" data-prosemirror-content-type="node" data-prosemirror-node-name="codeBlock" data-prosemirror-node-block="true"><div class="code-block--start" contenteditable="false"></div><div class="code-block-content-wrapper"><div contenteditable="false"><div class="code-block-gutter-pseudo-element" data-label="1
2
3
4
5
6
7"></div></div><div class="code-content"><code data-language="json" spellcheck="false" data-testid="code-block--code" aria-label="">  {
    "success": true,
    "message": null,
    "data": {
      // Backend Service에서 받은 실제 데이터
    }
  }</code></div></div><div class="code-block--end" contenteditable="false"></div></pre>

- 실패 응답:

<pre class="code-block" data-language="json" data-prosemirror-content-type="node" data-prosemirror-node-name="codeBlock" data-prosemirror-node-block="true"><div class="code-block--start" contenteditable="false"></div><div class="code-block-content-wrapper"><div contenteditable="false"><div class="code-block-gutter-pseudo-element" data-label="1
2
3
4"></div></div><div class="code-content"><code data-language="json" spellcheck="false" data-testid="code-block--code" aria-label="">  {
    "error": true,
    "message": "에러 메시지"
  }</code></div></div><div class="code-block--end" contenteditable="false"></div></pre>

**날짜/시간 형식:**

- ISO 8601 형식 사용 (YYYY-MM-DDTHH:mm:ss.sssZ)
- 모든 날짜는 UTC 기준으로 처리한다
- Frontend에서 로컬 시간으로 변환하여 표시한다

**에러 코드 체계:**

- {DOMAIN}{NUMBER} 형식 사용 (예: AUTH001, DATA003)
- 도메인별로 번호 범위를 할당한다
- 일관된 에러 코드를 유지한다

### 2.8 개발 범위 및 제약사항

**2.8.1 Agent 개발 범위 제한**

- Agent 개발 시 코드 추가 및 수정은 `src/services/` 디렉토리 하위에만 허용된다
- `src/services/` 외부의 기존 코드는 어떠한 경우에도 수정할 수 없다
- `src/services/` 외부에는 어떠한 경로(디렉토리) 또는 파일도 생성할 수 없다

**2.8.2 파일 생성 원칙**

- `src/services/` 하위에 새로운 하위 디렉토리를 생성할 수 없다
- 새로운 기능 구현 시 `src/services/` 디렉토리에 파일만 추가하여 개발한다
- 모든 신규 모듈은 `src/services/*.py` 형태로만 생성한다

**2.8.3 graph.py 구현 원칙**

- `src/services/graph.py`는 애플리케이션의 진입점이며 필수 파일이다
- `graph.py`에서 다른 모듈들을 import하여 전체 워크플로우를 구성한다
- 초기 예제 코드로 제공되므로, 실제 구현 시에는 spec에 맞춰 모든 기능을 재구현해야 한다
- 예제 코드의 구조는 참조하되, spec 요구사항에 맞게 완전히 새로 작성한다

**2.8.4 설정 관리 원칙**

- 설정 관리는 `.env` 파일의 데이터와 `src/core/config.py`만을 사용한다
- 개발 중 추가 환경변수가 필요한 경우, `src/services/` 하위에 별도의 설정 관리 파일을 생성한다
- `src/core/config.py`를 직접 수정하지 않으며, 필요한 설정은 `src/services/` 하위에서 관리한다
- 외부 설정 파일(예: YAML, JSON 등)을 생성하거나 읽지 않는다

## **3. 아키텍처 원칙**

### 3.1 계층 분리

- 각 계층은 명확한 책임을 갖는다
- 계층 간 통신은 정의된 인터페이스를 통해서만 한다
- 하위 계층은 상위 계층을 참조하지 않는다

### 3.2 데이터 접근 제약

- 데이터베이스 직접 연결을 금지한다
- 모든 데이터는 정의된 API를 통해서만 접근한다
- 계층을 건너뛰는 접근을 금지한다

### 3.3 책임 분리

- 각 컴포넌트는 단일 책임 원칙을 따른다
- UI 로직과 비즈니스 로직을 분리한다
- 데이터의 가공과 변환은 명확한 계층에서만 수행한다

### 3.4 느슨한 결합

- 컴포넌트 간 직접 의존을 최소화한다
- 인터페이스를 통한 통신을 원칙으로 한다
- 설정은 코드 외부에서 관리한다

## **4. 코드 품질 원칙**

### 4.1 가독성 우선

- 읽기 쉬운 코드를 작성한다
- 명확하고 의미 있는 이름을 사용한다
- 매직 넘버나 하드코딩을 지양한다

### 4.2 단순성 유지

- 불필요한 추상화를 피한다
- 과도한 최적화를 경계한다
- 복잡성은 반드시 정당한 이유가 있어야 한다

### 4.3 함수 설계 원칙

- 한 함수는 한 가지 일만 수행한다
- 재사용 가능한 로직은 공통 함수로 분리한다
- 함수 이름만으로도 무엇을 하는지 명확해야 한다
- 중복 코드는 즉시 제거하고 공통 함수로 추출한다

### 4.4 일관성 유지

- 일관된 코딩 스타일을 유지한다
- 네이밍 컨벤션을 준수한다
- 에러 처리 방식을 통일한다

### 4.5 테스트 가능성

- 테스트하기 어려운 코드는 리팩토링한다
- 의존성 주입을 활용한다
- 사이드 이펙트를 최소화한