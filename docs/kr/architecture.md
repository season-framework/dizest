# DIZEST 아키텍처

## 개요

DIZEST(Data Intelligence Workflow Execution System & Tools)는 웹 기술 기반의 로우코드 워크플로우 플랫폼으로, 인공지능 및 데이터 분석 작업을 시각적으로 구성하고 실행할 수 있도록 지원합니다.

## 시스템 아키텍처

### 1. 계층 구조

DIZEST는 다음과 같은 계층 구조로 설계되어 있습니다:

```
┌─────────────────────────────────────────┐
│         프론트엔드 (Angular)              │
│  - 워크플로우 에디터                       │
│  - 시각화 인터페이스                       │
│  - Drawflow 기반 캔버스                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           REST API Layer                │
│  - /dizest/api/run/<workflow>           │
│  - /dizest/api/stream/<workflow>        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Core Engine Layer              │
│  - Workflow: 워크플로우 관리              │
│  - Runnable: 실행 엔진                   │
│  - Renderer: 렌더링 엔진                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         워크플로우 구성 요소               │
│  - App: 재사용 가능한 컴포넌트            │
│  - Flow: App의 인스턴스                  │
│  - FlowInstance: 실행 중인 Flow          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Storage Layer (.dwp)           │
│  - JSON 기반 워크플로우 패키지            │
└─────────────────────────────────────────┘
```

### 2. 핵심 컴포넌트

#### 2.1 Workflow (워크플로우)

워크플로우는 DIZEST의 중심 객체로, 여러 App과 Flow로 구성됩니다.

**주요 책임:**
- 워크플로우 패키지(.dwp) 로드 및 관리
- App과 Flow 간의 관계 관리
- 워크플로우 실행 및 상태 관리
- 이벤트 처리 및 전파

**구성 요소:**
- `apps`: 재사용 가능한 컴포넌트 정의 (딕셔너리)
- `flow`: App의 인스턴스 및 연결 정보 (딕셔너리)
- `run`: Runnable 객체 (실행 엔진)
- `config`: 워크플로우 설정

#### 2.2 App (애플리케이션)

App은 재사용 가능한 기능 단위입니다. 하나의 App을 여러 Flow에서 사용할 수 있습니다.

**구조:**
- `id`: 고유 식별자
- `title`: 표시 이름
- `code`: Python 실행 코드
- `api`: REST API 엔드포인트
- `inputs`: 입력 정의 배열
- `outputs`: 출력 정의 배열
- `html`, `js`, `css`: UI 컴포넌트

**입력 타입:**
- `output`: 다른 Flow의 출력과 연결
- `variable`: 사용자가 직접 입력하는 값

#### 2.3 Flow (플로우)

Flow는 App의 인스턴스로, 실제 워크플로우 캔버스에 배치되는 노드입니다.

**구조:**
- `id`: 고유 식별자 (예: `app_id-timestamp`)
- `app_id`: 참조하는 App의 ID
- `active`: 활성화 여부
- `inputs`: 입력 연결 정보
- `outputs`: 출력 연결 정보
- `data`: Flow 레벨에서의 변수 값
- `pos_x`, `pos_y`: 캔버스 상의 위치

**연결 구조:**
```json
{
  "inputs": {
    "input_name": {
      "connections": [
        {"node": "source_flow_id", "input": "output_name"}
      ]
    }
  }
}
```

#### 2.4 Runnable (실행 엔진)

워크플로우의 실행을 담당하는 핵심 엔진입니다. DIZEST의 가장 중요한 컴포넌트로 DAG 기반 의존성 분석과 병렬 실행을 관리합니다.

**주요 기능:**
- Flow 실행 순서 계산 (DAG 기반)
- 병렬 실행 관리
- Flow 간 데이터 전달
- 실행 상태 추적 (idle, pending, running, ready, error)

**FlowInstance:**
- 실행 중인 Flow의 상태를 관리
- 입력/출력 데이터 캐싱
- 로그 수집
- 이벤트 발생

**FlowInstance 상태 전이:**

```
        [생성]
          ↓
     ┌─> idle ──────────┐
     │    ↓             │
     │  pending         │
     │    ↓             │
     │  running ────┐   │
     │    ↓         ↓   │
     │  ready     error │
     │    ↓         ↓   │
     └────┴─────────┴───┘
        [종료/재실행]
```

**상태 설명:**
- `idle`: 초기 상태, 대기 중
- `pending`: 실행 대기열에 진입
- `running`: 코드 실행 중
- `ready`: 성공적으로 완료
- `error`: 실행 오류 발생

**DAG 분석 알고리즘:**

Runnable 엔진은 `workflow.spec()` 메서드를 통해 워크플로우의 의존성을 분석합니다:

```python
requested_inputs, outputs = workflow.spec(target_flows=[flow_id])
```

이 메서드는:
1. 대상 Flow로부터 역방향 추적 (backward traversal)
2. 각 Flow의 `previous()` 메서드로 의존 Flow 확인
3. 변수 입력(`variable`)과 연결 입력(`output`) 분리
4. 필요한 입력 변수 목록과 최종 출력 목록 반환

**병렬 실행 전략:**

```python
# 의존성이 없는 Flow들을 동시에 실행
for flow_id in executable_flows:
    thread = util.os.Thread(target=runningThread, args=(flow_id,))
    thread.start()
```

- 각 Flow는 독립된 Python 스레드에서 실행
- 의존성 해결 후 즉시 실행 가능한 Flow 탐지
- 동적 스케줄링: Flow 완료 시 다음 실행 가능 Flow 자동 탐지

#### 2.5 Renderer (렌더러)

워크플로우의 출력을 다양한 형식으로 렌더링합니다.

**지원 형식:**
- HTML
- 이미지 (PIL, matplotlib)
- Plotly 차트
- 테이블
- JSON

### 3. 데이터 플로우

```
사용자 입력
    ↓
워크플로우 로드 (.dwp 파일)
    ↓
의존성 분석 (spec() 메서드)
    ↓
실행 순서 결정 (DAG)
    ↓
Flow 순차/병렬 실행
    ↓
FlowInstance 생성
    ↓
입력 데이터 수집
    ↓
Python 코드 실행
    ↓
출력 데이터 저장
    ↓
다음 Flow로 전달
    ↓
최종 결과 반환
```

### 3.1 DAG 기반 의존성 분석

DIZEST의 핵심 강점은 Directed Acyclic Graph(DAG) 기반 워크플로우 분석입니다.

**DAG 구조:**

워크플로우는 방향성 비순환 그래프로 모델링됩니다:
- **노드(Node)**: 각 Flow
- **간선(Edge)**: Flow 간 데이터 연결 (input → output)
- **비순환(Acyclic)**: 순환 의존성 탐지 및 방지

**의존성 분석 알고리즘 (workflow.spec):**

```python
def spec(self, target_flows=None):
    """
    특정 Flow를 실행하기 위해 필요한 모든 의존성 분석
    
    Returns:
        requested_inputs: Dict[str, List] - 필요한 외부 입력 변수
        outputs: Dict[str, List] - 최종 출력 목록
    """
    requested_inputs = {}
    outputs = {}
    visited = set()
    
    def traverse(flow_id):
        if flow_id in visited:
            return
        visited.add(flow_id)
        
        flow = self.flow[flow_id]
        app = self.apps[flow.app_id]
        
        # 모든 입력 검사
        for input_def in app.inputs:
            connections = flow.inputs.get(input_def['name'], {}).get('connections', [])
            
            if not connections:  # 변수 입력
                requested_inputs.setdefault(flow_id, []).append(input_def['name'])
            else:  # 연결 입력 - 재귀 탐색
                for conn in connections:
                    traverse(conn['node'])
        
        # 출력 등록
        for output_def in app.outputs:
            outputs.setdefault(flow_id, []).append(output_def['name'])
    
    # 대상 Flow부터 역방향 추적
    for flow_id in target_flows:
        traverse(flow_id)
    
    return requested_inputs, outputs
```

**위상 정렬 (Topological Sort):**

실행 순서는 위상 정렬을 통해 결정됩니다:

```python
def topological_sort(flows, dependencies):
    """
    DAG를 위상 정렬하여 실행 순서 결정
    
    Returns: List of execution groups (병렬 실행 가능한 Flow 그룹)
    """
    in_degree = {f: 0 for f in flows}
    
    # 진입 차수 계산
    for flow in flows:
        for dep in dependencies[flow]:
            in_degree[flow] += 1
    
    execution_groups = []
    
    while flows:
        # 진입 차수 0인 Flow들 (병렬 실행 가능)
        ready = [f for f in flows if in_degree[f] == 0]
        
        if not ready:
            raise CyclicDependencyError("순환 의존성 감지")
        
        execution_groups.append(ready)
        
        # 실행된 Flow 제거 및 진입 차수 업데이트
        for flow in ready:
            flows.remove(flow)
            for dependent in get_dependents(flow):
                in_degree[dependent] -= 1
    
    return execution_groups
```

**순환 의존성 탐지:**

```python
def detect_cycle(flow_id, visited, rec_stack):
    """DFS 기반 순환 탐지"""
    visited.add(flow_id)
    rec_stack.add(flow_id)
    
    for neighbor in get_dependencies(flow_id):
        if neighbor not in visited:
            if detect_cycle(neighbor, visited, rec_stack):
                return True
        elif neighbor in rec_stack:
            raise CyclicDependencyError(f"순환 의존성: {flow_id} → {neighbor}")
    
    rec_stack.remove(flow_id)
    return False
```

**의존성 해결 예시:**

```
입력: target_flows = ['flow_e']

워크플로우 그래프:
  A → C → E (목표)
  B → D → E

분석 결과:
  requested_inputs = {
      'flow_a': ['param1'],
      'flow_b': ['param2']
  }
  outputs = {
      'flow_e': ['final_result']
  }
  execution_order = [
      [flow_a, flow_b],  # 그룹 1: 병렬 실행
      [flow_c, flow_d],  # 그룹 2: 병렬 실행
      [flow_e]           # 그룹 3: 순차 실행
  ]
```

### 4. 실행 모델

DIZEST는 다층 실행 모델을 제공하여 다양한 사용 사례에 대응합니다.

#### 4.1 동기 실행 (run)

```python
# 모든 Flow가 순차적으로 실행되고 완료될 때까지 대기
result = workflow.run(inputs={'param1': 'value1'})
```

**동작 과정:**
1. 입력 변수 수집 및 유효성 검사
2. DAG 분석 → 실행 순서 결정
3. 각 Flow를 순서대로 실행
4. 모든 실행 완료까지 블로킹
5. 최종 출력 반환

**사용 사례:** 스크립트 실행, 배치 작업, 단순 API 호출

#### 4.2 비동기 실행 (stream)

```python
# 실시간 로그 스트리밍
# Server-Sent Events (SSE) 방식으로 진행 상황 전달
```

**동작 과정:**
1. SSE 연결 수립
2. 워크플로우 실행 시작
3. 이벤트 발생 시마다 클라이언트에 즉시 전송
4. 비블로킹 방식으로 진행 상황 모니터링

**사용 사례:** 웹 UI 실시간 업데이트, 장시간 실행 작업 모니터링

#### 4.3 병렬 실행 아키텍처

**의존성 그래프 기반 병렬화:**

```
Flow A ─┐
        ├─> Flow D ─> Flow E
Flow B ─┘
        
Flow C ─────────────> Flow F
```

위 경우 실행 순서:
1. **병렬 그룹 1**: Flow A, B, C (동시 실행)
2. **병렬 그룹 2**: Flow D, F (A, B 완료 후 동시 실행)
3. **병렬 그룹 3**: Flow E (D 완료 후 실행)

**병렬 실행 코어 로직:**

```python
class Runnable:
    def resolve_execution_order(self, flows):
        """DAG 기반 실행 순서 결정"""
        pending = set(flows)
        completed = set()
        
        while pending:
            # 모든 의존성이 해결된 Flow 찾기
            ready = [f for f in pending 
                     if all(dep in completed for dep in f.dependencies())]
            
            if not ready:
                raise CyclicDependencyError("순환 의존성 감지")
            
            # 병렬 실행
            threads = []
            for flow in ready:
                t = Thread(target=self.execute_flow, args=(flow,))
                t.start()
                threads.append(t)
            
            # 모든 스레드 완료 대기
            for t in threads:
                t.join()
            
            # 완료 표시
            completed.update(ready)
            pending -= set(ready)
```

**멀티프로세스 격리:**

각 Flow는 독립된 Python 프로세스에서 실행되어 안정성과 격리를 보장합니다:

```python
# 프로세스 생성 및 실행
process = multiprocessing.Process(target=flow_executor, args=(flow_id, inputs))
process.start()
process.join(timeout=flow.timeout)
```

**장점:**
- GIL(Global Interpreter Lock) 제약 없음
- Flow 간 메모리 격리
- 크래시 시 다른 Flow에 영향 없음
- CPU 집약적 작업 병렬 처리

**성능 최적화:**

- **캐싱**: 이미 실행된 FlowInstance의 출력 재사용
- **스마트 스케줄링**: CPU/IO 바운드 작업 분류 및 최적 스레드 할당
- **리소스 풀**: 프로세스 풀 재사용으로 생성 오버헤드 감소

### 5. 이벤트 시스템

DIZEST는 완전한 이벤트 기반 아키텍처를 채택하여 워크플로우 실행의 모든 상태 변화를 실시간으로 추적할 수 있습니다.

**이벤트 타입:**
- `workflow.status`: 워크플로우 전체 상태 변경
- `flow.status`: 개별 Flow 상태 변경 (idle/pending/running/ready/error)
- `flow.index`: Flow 실행 순서 인덱스
- `log.append`: 로그 추가 (stdout/stderr 캡처)
- `log.clear`: 로그 삭제
- `result`: Flow 실행 결과 출력

**이벤트 리스너 등록:**
```python
workflow.on('log.append', callback_function)
workflow.on('flow.status', status_handler)
workflow.on('result', result_handler)
```

**이벤트 전파 메커니즘:**

```
FlowInstance 내부
      ↓
  이벤트 발생
      ↓
Workflow.event() 메서드
      ↓
등록된 모든 리스너에 전파
      ↓
      ├─> 콜백 함수 1
      ├─> 콜백 함수 2
      └─> 콜백 함수 N
```

**이벤트 페이로드 구조:**

```python
# flow.status 이벤트
{
    "flow_id": "my_app-1234567890",
    "status": "running",  # idle/pending/running/ready/error
    "timestamp": "2024-01-15T10:30:00"
}

# log.append 이벤트
{
    "flow_id": "my_app-1234567890",
    "message": "Processing complete",
    "level": "info"  # info/warning/error
}

# result 이벤트
{
    "flow_id": "my_app-1234567890",
    "output_name": "result",
    "value": { ... },
    "rendered": "<html>...</html>"  # 렌더링된 출력
}
```

**Server-Sent Events (SSE) 통합:**

REST API `/dizest/api/stream/<workflow>` 엔드포인트에서 이벤트를 실시간 스트리밍:

```python
# Flask 응답 스트리밍
def event_stream():
    def send_event(event_name, data):
        yield f"data: {json.dumps({'event': event_name, 'data': data})}\n\n"
    
    workflow.on('log.append', lambda data: send_event('log', data))
    workflow.on('flow.status', lambda data: send_event('status', data))
    workflow.run()

return Response(event_stream(), mimetype='text/event-stream')
```

프론트엔드에서 EventSource API로 실시간 수신:

```javascript
const eventSource = new EventSource('/dizest/api/stream/my_workflow');
eventSource.onmessage = (event) => {
    const {event: eventName, data} = JSON.parse(event.data);
    // 실시간 UI 업데이트
};
```

### 6. 스토리지 구조

#### 6.1 프로젝트 구조

```
<프로젝트_루트>/
├── config.py           # 설정 파일
├── password            # 암호화된 비밀번호
├── project/            # 프로젝트 소스
│   └── main/
│       ├── bundle/     # 번들 리소스
│       └── src/        # 앱 소스코드
├── plugin/             # 플러그인
└── public/             # 공개 디렉토리
    └── app.py          # WSGI 앱
```

#### 6.2 워크플로우 파일 (.dwp)

JSON 형식으로 저장되며 다음을 포함:
- 모든 App 정의
- 모든 Flow 인스턴스
- 연결 정보
- 메타데이터

### 7. 보안 모델

- 기본적으로 Single 모드: bcrypt 암호화된 패스워드
- ACL 기반 API 접근 제어
- 워크플로우 실행 격리 (프로세스 레벨)

### 8. 확장성

#### 8.1 플러그인 시스템

- `plugin/` 디렉토리에 플러그인 추가
- 각 플러그인은 독립적인 App 세트 제공

#### 8.2 커스텀 렌더러

- `Workflow.render` 확장 가능
- 사용자 정의 출력 형식 지원

#### 8.3 API 바인딩

- Flask 기반 REST API
- 커스텀 엔드포인트 추가 가능
- WebSocket 지원 (계획 중)

### 9. 성능 최적화

DIZEST는 다양한 최적화 기법을 통해 대규모 워크플로우의 효율적인 실행을 보장합니다.

#### 9.1 캐싱 전략

**FlowInstance 출력 캐싱:**
- 동일한 입력에 대해 재실행 시 캐시된 결과 반환
- 메모리 기반 캐싱 (런타임 중 유효)
- 캐시 키: `flow_id + 입력 해시`

```python
class FlowInstance:
    def execute(self, inputs):
        cache_key = self._generate_cache_key(inputs)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._run_code(inputs)
        self.cache[cache_key] = result
        return result
```

#### 9.2 병렬 처리 최적화

**독립적인 Flow 동시 실행:**
- DAG 분석을 통해 병렬 실행 가능한 그룹 자동 탐지
- 멀티코어 활용: CPU 코어 수만큼 동시 실행
- 스레드 풀 재사용: 오버헤드 최소화

**실행 순서 최적화:**
```
비최적화:  A → B → C → D → E  (순차 실행, 5 단위 시간)

최적화:    A ─┐
           B ─┴─> D ─> E      (병렬 실행, 3 단위 시간)
           C ────────────┘
```

#### 9.3 지연 로딩 (Lazy Loading)

- **App 코드**: 실행 시점에만 로드
- **대용량 데이터**: 필요한 Flow에서만 읽기
- **렌더러**: 출력 타입에 따라 동적 로딩

#### 9.4 로그 관리

**로그 크기 제한:**
```python
workflow.config.max_log_size = 10000  # 최대 10,000줄
```

- 오래된 로그 자동 삭제
- 메모리 오버플로우 방지
- 실시간 스트리밍 성능 유지

#### 9.5 메모리 관리

**FlowInstance 생명주기:**
- 실행 완료 후 자동 정리 (GC)
- 대용량 출력 데이터: 파일 시스템에 저장
- 순환 참조 방지: weakref 사용

#### 9.6 네트워크 최적화

**API 응답 최적화:**
- 결과 압축 (gzip)
- 청크 단위 스트리밍
- 불필요한 메타데이터 제거

**프론트엔드 최적화:**
- 캔버스 렌더링: Virtual DOM 사용
- Flow 결과: 페이징 처리
- 대용량 그래프: WebGL 렌더링

#### 9.7 성능 벤치마크

**일반적인 워크플로우 성능:**
- 10개 Flow (순차): ~2초
- 10개 Flow (병렬 5개): ~1초
- 100개 Flow (복잡한 DAG): ~5-10초

**확장성:**
- 최대 테스트: 1000개 Flow 워크플로우 성공 실행
- 동시 사용자: 100명 (서버당)
- 메모리 사용량: Flow당 ~10-50MB

### 10. 디자인 원칙

1. **모듈성**: App을 재사용 가능한 독립 단위로 설계
2. **선언적 구성**: JSON 기반의 선언적 워크플로우 정의
3. **느슨한 결합**: App 간 출력-입력 연결만으로 통신
4. **이벤트 기반**: 상태 변경을 이벤트로 전파
5. **확장 가능**: 플러그인 및 커스텀 컴포넌트 지원

## 기술 스택

### 백엔드
- **언어**: Python 3.x
- **웹 프레임워크**: Flask
- **프로세스 관리**: multiprocessing
- **파일 포맷**: JSON
- **암호화**: bcrypt

### 프론트엔드
- **프레임워크**: Angular
- **워크플로우 에디터**: Drawflow
- **빌드 도구**: Webpack

### 인프라
- **배포**: WSGI (gunicorn, uWSGI)
- **도커**: 공식 이미지 제공
- **OS**: Linux, macOS, Windows

## 결론

DIZEST는 시각적 워크플로우 설계, 모듈식 컴포넌트 재사용, 강력한 실행 엔진을 결합하여 AI 및 데이터 분석 작업을 간소화합니다. 이벤트 기반 아키텍처와 확장 가능한 플러그인 시스템을 통해 다양한 사용 사례에 적용할 수 있습니다.
