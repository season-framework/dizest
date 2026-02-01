# Workflow 클래스 API 레퍼런스

## 개요

`Workflow` 클래스는 DIZEST의 핵심 클래스로, 워크플로우 패키지를 로드하고 관리하며 실행하는 기능을 제공합니다.

## 클래스 정의

```python
from dizest import Workflow

workflow = Workflow(package, **kwargs)
```

## 생성자

### `__init__(package, **kwargs)`

워크플로우 객체를 생성합니다.

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `package` | `str` 또는 `dict` | ✓ | - | 워크플로우 파일 경로(.dwp) 또는 워크플로우 딕셔너리 |
| `cwd` | `str` | ✗ | `os.getcwd()` | 워크플로우 작업 디렉토리 |
| `max_log_size` | `int` | ✗ | `50` | 각 Flow가 유지할 최대 로그 항목 수 |
| `event` | `dict` | ✗ | `{}` | 이벤트 핸들러 딕셔너리 |

#### 예제

```python
# 파일 경로로 로드
workflow = Workflow("myworkflow.dwp")

# 작업 디렉토리 지정
workflow = Workflow("myworkflow.dwp", cwd="/path/to/workdir")

# 로그 크기 제한
workflow = Workflow("myworkflow.dwp", max_log_size=100)

# 딕셔너리로 직접 로드
package = {
    "apps": {...},
    "flow": {...}
}
workflow = Workflow(package)
```

---

## 속성

### `config`

워크플로우 설정 객체입니다.

**타입**: `Config`

**속성**:
- `cwd`: 작업 디렉토리
- `max_log_size`: 최대 로그 크기
- `event`: 이벤트 핸들러 딕셔너리

### `run`

워크플로우 실행 엔진입니다.

**타입**: `Runnable`

### `render`

워크플로우 렌더러입니다.

**타입**: `Renderer`

---

## 메서드

### 워크플로우 관리

#### `load(package)`

워크플로우 패키지를 로드합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `package` | `str` 또는 `dict` | 워크플로우 파일 경로 또는 딕셔너리 |

##### 반환값

`Workflow` - self 객체

##### 예외

- `Exception`: `apps` 또는 `flow` 키가 없는 경우

##### 예제

```python
workflow = Workflow({"apps": {}, "flow": {}})
workflow.load("updated_workflow.dwp")
```

---

#### `to_dict()`

워크플로우를 딕셔너리로 반환합니다.

##### 반환값

`dict` - 워크플로우 패키지 딕셔너리

##### 예제

```python
package = workflow.to_dict()
print(package.keys())  # dict_keys(['apps', 'flow', ...])
```

---

### App 관리

#### `apps()`

워크플로우의 모든 App ID 목록을 반환합니다.

##### 반환값

`list` - App ID 문자열 리스트

##### 예제

```python
app_ids = workflow.apps()
# ['app_id_1', 'app_id_2', ...]
```

---

#### `app(app_id)`

특정 App 객체를 반환합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `app_id` | `str` | App의 고유 ID |

##### 반환값

`App` - App 객체 (존재하지 않으면 `None`)

##### 예제

```python
app = workflow.app("my_app_id")
if app:
    print(app.title())
```

---

### Flow 관리

#### `flows()`

워크플로우의 모든 Flow 객체 목록을 반환합니다.

##### 반환값

`list` - Flow 객체 리스트

##### 예제

```python
flows = workflow.flows()
for flow in flows:
    print(flow.id(), flow.title())
```

---

#### `flow(flow_id)`

특정 Flow 객체를 반환합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `flow_id` | `str` | Flow의 고유 ID |

##### 반환값

`Flow` - Flow 객체 (존재하지 않으면 `None`)

##### 예제

```python
flow = workflow.flow("app_id-1234567890")
if flow:
    print(f"Active: {flow.active()}")
```

---

### 이벤트 처리

#### `on(name, fn)`

이벤트 리스너를 등록합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `name` | `str` | 이벤트 이름 (`'*'`는 모든 이벤트) |
| `fn` | `callable` | 이벤트 핸들러 함수 |

##### 이벤트 타입

| 이벤트 이름 | 설명 | 콜백 시그니처 |
|-----------|------|--------------|
| `workflow.status` | 워크플로우 전체 상태 변경 | `fn(flow_id, event_name, value)` |
| `flow.status` | Flow 상태 변경 | `fn(flow_id, event_name, value)` |
| `flow.index` | Flow 실행 순서 인덱스 | `fn(flow_id, event_name, value)` |
| `log.append` | 로그 추가 | `fn(flow_id, event_name, value)` |
| `log.clear` | 로그 삭제 | `fn(flow_id, event_name, value)` |
| `result` | 결과 출력 | `fn(flow_id, event_name, value)` |
| `*` | 모든 이벤트 | `fn(flow_id, event_name, value)` |

##### Flow 상태 값

- `idle`: 대기 중
- `pending`: 준비 중
- `running`: 실행 중
- `ready`: 완료
- `error`: 오류 발생

##### 예제

```python
# 로그 이벤트 리스너
def on_log(flow_id, event_name, log_message):
    print(f"[{flow_id}] {log_message}")

workflow.on('log.append', on_log)

# 상태 변경 리스너
def on_status(flow_id, event_name, status):
    print(f"Flow {flow_id}: {status}")

workflow.on('flow.status', on_status)

# 모든 이벤트 리스너
def on_all(flow_id, event_name, value):
    print(f"Event: {event_name} from {flow_id}")

workflow.on('*', on_all)
```

---

### 워크플로우 분석

#### `spec()`

워크플로우의 입출력 스펙을 분석합니다.

##### 반환값

`tuple` - `(requested, outputs)`
- `requested`: 필요한 입력 딕셔너리 `{flow_id: {input_name: None}}`
- `outputs`: 제공되는 출력 딕셔너리 `{flow_id: [output_name1, output_name2, ...]}`

##### 예제

```python
requested, outputs = workflow.spec()

# 필요한 외부 입력 확인
print("Required inputs:", requested)
# {'flow_1': {'param1': None, 'param2': None}}

# 최종 출력 확인
print("Available outputs:", outputs)
# {'flow_3': ['result', 'summary']}
```

---

## 실행 (Runnable 메서드)

워크플로우 실행은 `workflow.run` 객체를 통해 수행됩니다.

### `workflow.run(flow=None, threaded=False, **kwargs)`

워크플로우를 실행합니다.

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `flow` | `Flow` | ✗ | `None` | 실행할 Flow (None이면 전체 워크플로우) |
| `threaded` | `bool` | ✗ | `False` | 백그라운드 실행 여부 |
| `**kwargs` | `dict` | ✗ | `{}` | Flow에 전달할 입력 파라미터 |

#### 반환값

- `threaded=False`: 블로킹 실행, 완료 후 반환
- `threaded=True`: `multiprocessing.Process` 객체 반환

#### 예제

```python
# 전체 워크플로우 동기 실행
workflow.run()

# 특정 Flow만 실행
flow = workflow.flow("flow_id")
workflow.run(flow)

# 파라미터 전달
workflow.run(flow, message="Hello", count=10)

# 비동기 실행
process = workflow.run(flow, threaded=True)
process.join()  # 완료 대기
```

---

### `workflow.run.status()`

워크플로우 전체 실행 상태를 반환합니다.

#### 반환값

`str` - 워크플로우 상태
- `idle`: 모든 Flow가 대기 중
- `pending`: 일부 Flow가 준비 중
- `running`: 일부 Flow가 실행 중
- `ready`: 모든 Flow가 완료
- `error`: 일부 Flow에서 오류 발생

#### 예제

```python
status = workflow.run.status()
print(f"Workflow status: {status}")
```

---

### `workflow.run.instance(flow)`

특정 Flow의 실행 인스턴스를 반환합니다.

#### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `flow` | `Flow` | Flow 객체 |

#### 반환값

`FlowInstance` - Flow 실행 인스턴스 객체

#### 예제

```python
flow = workflow.flow("flow_id")
instance = workflow.run.instance(flow)

# 실행 상태 확인
print(instance.status())

# 로그 확인
for log in instance.log():
    print(log)

# 출력 데이터 확인
output_data = instance.output_data
print(output_data)
```

---

### `workflow.run.stop()`

실행 중인 워크플로우를 중지합니다.

#### 예제

```python
# 워크플로우 시작
workflow.run(threaded=True)

# 중지
workflow.run.stop()
```

---

### `workflow.run.sync()`

모든 Flow 인스턴스의 상태를 동기화하여 반환합니다.

#### 반환값

`dict` - Flow 상태 딕셔너리 `{flow_id: {'status': ..., 'index': ..., 'log': [...]}}`

#### 예제

```python
sync_data = workflow.run.sync()
for flow_id, data in sync_data.items():
    print(f"{flow_id}: {data['status']}")
```

---

## 렌더링

### `workflow.render(value, **kwargs)`

값을 렌더링 가능한 형식으로 변환합니다.

#### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `value` | `any` | 렌더링할 값 |
| `**kwargs` | `dict` | 추가 옵션 |

#### 지원 타입

- `str`: 문자열 (HTML 가능)
- `dict`, `list`: JSON
- `pandas.DataFrame`: HTML 테이블
- `matplotlib.figure.Figure`: Base64 이미지
- `plotly.graph_objs.Figure`: Plotly JSON
- `PIL.Image`: Base64 이미지

#### 반환값

렌더링된 결과 (문자열 또는 딕셔너리)

#### 예제

```python
import pandas as pd

df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
html = workflow.render(df)
print(html)  # HTML 테이블
```

---

## 사용 예제

### 기본 사용

```python
import dizest

# 워크플로우 로드
workflow = dizest.Workflow("myworkflow.dwp")

# 이벤트 리스너 등록
workflow.on('log.append', lambda fid, e, log: print(log))

# 실행
workflow.run()

# 결과 확인
requested, outputs = workflow.spec()
for flow_id in outputs:
    flow = workflow.flow(flow_id)
    instance = workflow.run.instance(flow)
    print(f"Output: {instance.output_data}")
```

### 파라미터 전달

```python
# 필요한 입력 확인
requested, outputs = workflow.spec()

# 입력 제공
params = {
    'param1': 'value1',
    'param2': 100
}

# 실행
for flow_id in requested:
    flow = workflow.flow(flow_id)
    workflow.run(flow, **params)
```

### 조건부 실행

```python
# 특정 Flow만 활성화
for flow in workflow.flows():
    if "test" in flow.title():
        flow.update(active=True)
    else:
        flow.update(active=False)

# 활성 Flow만 실행
workflow.run()
```

---

## 관련 문서

- [Flow 클래스 API](flow.md)
- [App 클래스 API](app.md)
- [FlowInstance 클래스 API](flowinstance.md)
- [사용 가이드](../usage-guide.md)
