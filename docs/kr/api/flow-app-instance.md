# Flow, App, FlowInstance 클래스 API 레퍼런스

## 목차

1. [Flow 클래스](#flow-클래스)
2. [App 클래스](#app-클래스)
3. [FlowInstance 클래스](#flowinstance-클래스)

---

## Flow 클래스

Flow는 워크플로우 캔버스에 배치된 App의 인스턴스입니다.

### 개요

```python
flow = workflow.flow(flow_id)
```

### 메서드

#### `id()`

Flow의 고유 식별자를 반환합니다.

##### 반환값

`str` - Flow ID (예: `app_id-1234567890`)

##### 예제

```python
flow_id = flow.id()
print(flow_id)  # "my_app-1706123456789"
```

---

#### `title()`

Flow의 표시 이름을 반환합니다.

##### 반환값

`str` - Flow 제목 (설정되지 않은 경우 App의 제목)

##### 예제

```python
title = flow.title()
print(title)  # "My Custom Flow"
```

---

#### `active()`

Flow의 활성화 상태를 확인합니다.

##### 반환값

`bool` - `True`이면 활성, `False`이면 비활성

##### 예제

```python
if flow.active():
    print("This flow will be executed")
else:
    print("This flow is disabled")
```

---

#### `app()`

Flow가 참조하는 App 객체를 반환합니다.

##### 반환값

`App` - App 객체

##### 예제

```python
app = flow.app()
print(f"App title: {app.title()}")
print(f"App code:\n{app.code()}")
```

---

#### `inputs()`

Flow의 입력 정보를 반환합니다.

##### 반환값

`dict` - 입력 딕셔너리
```python
{
    "input_name": {
        "type": "output" 또는 "variable",
        "data": [...] 또는 값,
        "inputtype": "text" | "number" | ...  # variable 타입인 경우
    }
}
```

**입력 타입:**
- `output`: 다른 Flow의 출력과 연결
  - `data`: `[[source_flow_id, output_name], ...]`
- `variable`: 사용자 입력 값
  - `data`: 입력된 값
  - `inputtype`: 입력 필드 타입

##### 예제

```python
inputs = flow.inputs()

for name, info in inputs.items():
    if info['type'] == 'output':
        print(f"{name}: connected to {info['data']}")
    else:
        print(f"{name}: value = {info['data']}")

# 출력 예:
# data: connected to [['flow_1', 'result']]
# message: value = Hello World
```

---

#### `previous()`

현재 Flow의 이전 단계 Flow ID 목록을 반환합니다.

##### 반환값

`list` - 이전 Flow ID 문자열 리스트

##### 예제

```python
prev_flows = flow.previous()
print(f"This flow depends on: {prev_flows}")
# ['flow_1', 'flow_2']
```

---

#### `package()`

Flow의 원시 패키지 딕셔너리를 반환합니다.

##### 반환값

`dict` - Flow 패키지 데이터

##### 예제

```python
pkg = flow.package()
print(pkg.keys())
# dict_keys(['id', 'app_id', 'active', 'inputs', 'outputs', 'data', 'pos_x', 'pos_y', ...])
```

---

#### `update(**kwargs)`

Flow 속성을 업데이트합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `**kwargs` | dict | 업데이트할 속성 딕셔너리 |

##### 예제

```python
# Flow 비활성화
flow.update(active=False)

# Flow 제목 변경
flow.update(title="Updated Title")

# 여러 속성 동시 변경
flow.update(
    active=True,
    title="New Title",
    description="Updated description"
)
```

---

## App 클래스

App은 재사용 가능한 코드 블록으로, 여러 Flow에서 사용할 수 있습니다.

### 개요

```python
app = workflow.app(app_id)
# 또는
app = flow.app()
```

### 메서드

#### `id()`

App의 고유 식별자를 반환합니다.

##### 반환값

`str` - App ID

##### 예제

```python
app_id = app.id()
print(app_id)  # "my_custom_app"
```

---

#### `title()`

App의 제목을 반환합니다.

##### 반환값

`str` - App 제목 (없으면 `"Unknown"`)

##### 예제

```python
title = app.title()
print(title)  # "Data Processor"
```

---

#### `code()`

App의 Python 코드를 반환합니다.

##### 반환값

`str` - Python 코드

##### 예제

```python
code = app.code()
print(code)
# output:
# data = dizest.input("data", [])
# result = [x * 2 for x in data]
# dizest.output("result", result)
```

---

#### `api()`

App의 REST API 코드를 반환합니다.

##### 반환값

`str` - API 코드

##### 예제

```python
api_code = app.api()
if api_code:
    print("This app has API endpoint")
```

---

#### `inputs()`

App의 입력 정의를 반환합니다.

##### 반환값

`list` - 입력 정의 리스트
```python
[
    {
        "type": "output" 또는 "variable",
        "name": "input_name",
        "inputtype": "text" | "number" | ...  # variable 타입인 경우
    }
]
```

##### 예제

```python
inputs = app.inputs()
for inp in inputs:
    print(f"{inp['name']} ({inp['type']})")

# 출력:
# data (output)
# message (variable)
# count (variable)
```

---

#### `outputs()`

App의 출력 이름 목록을 반환합니다.

##### 반환값

`list` - 출력 이름 문자열 리스트

##### 예제

```python
outputs = app.outputs()
print(f"This app outputs: {outputs}")
# ['result', 'summary', 'status']
```

---

#### `update(**kwargs)`

App 속성을 업데이트합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `**kwargs` | dict | 업데이트할 속성 딕셔너리 |

##### 예제

```python
# 코드 업데이트
app.update(code="""
data = dizest.input("data")
processed = process(data)
dizest.output("result", processed)
""")

# 제목과 설명 업데이트
app.update(
    title="Updated App",
    description="New description"
)
```

---

## FlowInstance 클래스

FlowInstance는 실행 중인 Flow의 상태를 관리하는 객체입니다.

### 개요

```python
instance = workflow.run.instance(flow)
```

### 속성

| 속성 | 타입 | 설명 |
|-----|------|------|
| `flow` | `Flow` | 연결된 Flow 객체 |
| `data` | `dict` | 입력 데이터 |
| `output_data` | `dict` | 출력 데이터 |
| `timestamp` | `float` | 생성 시간 (Unix timestamp) |
| `process` | `Process` | 실행 프로세스 객체 |

### 메서드

#### `status(value=None)`

Flow 실행 상태를 조회하거나 설정합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `value` | `str` 또는 `None` | 설정할 상태 (None이면 조회) |

##### 상태 값

- `idle`: 대기 중
- `pending`: 준비 중
- `running`: 실행 중
- `ready`: 완료
- `error`: 오류 발생

##### 반환값

`str` - 현재 상태

##### 예제

```python
# 상태 조회
current_status = instance.status()
print(current_status)  # "running"

# 상태 변경
instance.status("ready")
```

---

#### `index(value=None)`

Flow 실행 순서 인덱스를 조회하거나 설정합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `value` | `int` 또는 `None` | 설정할 인덱스 (None이면 조회) |

##### 반환값

`int` - 실행 순서 인덱스

##### 예제

```python
idx = instance.index()
print(f"Execution order: {idx}")
```

---

#### `log(value=None)`

로그 메시지를 조회하거나 추가합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `value` | `str` 또는 `None` | 추가할 로그 메시지 (None이면 조회) |

##### 반환값

`list` - 로그 메시지 리스트

##### 예제

```python
# 로그 추가
instance.log("Processing started")
instance.log("Data loaded successfully")

# 로그 조회
logs = instance.log()
for log in logs:
    print(log)
```

---

#### `clear()`

로그를 삭제합니다.

##### 예제

```python
instance.clear()
```

---

#### `input(name, default=None)`

입력 값을 조회합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `name` | `str` | 입력 이름 |
| `default` | `any` | 기본값 (입력이 없을 경우) |

##### 반환값

입력 값 (연결된 출력 또는 변수 값)

##### 예제

```python
# 기본 사용
data = instance.input("data", default=[])

# 숫자 입력 (자동 형변환)
count = instance.input("count", default=0)

# 문자열 입력
message = instance.input("message", default="Hello")
```

---

#### `inputs(name)`

특정 입력에 연결된 모든 출력 값 리스트를 반환합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `name` | `str` | 입력 이름 |

##### 반환값

`list` - 연결된 모든 출력 값의 리스트

##### 예제

```python
# 여러 Flow의 출력이 하나의 입력에 연결된 경우
all_data = instance.inputs("data")
# [data1, data2, data3]

# 합계 계산
total = sum(all_data)
```

---

#### `output(*args, **kwargs)`

출력 값을 설정하거나 조회합니다.

##### 사용법 1: 단일 값 조회

```python
value = instance.output("result")
```

##### 사용법 2: 단일 값 설정

```python
instance.output("result", value)
```

##### 사용법 3: 여러 값 설정

```python
instance.output(result=value1, summary=value2)
```

##### 예제

```python
# 출력 설정
instance.output("result", [1, 2, 3])
instance.output("status", "success")

# 여러 출력 동시 설정
instance.output(
    result=[1, 2, 3],
    status="success",
    count=3
)

# 출력 조회
result = instance.output("result")
print(result)  # [1, 2, 3]
```

---

#### `result(name, value, **kwargs)`

결과를 렌더링하여 출력합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `name` | `str` | 결과 이름 |
| `value` | `any` | 결과 값 |
| `**kwargs` | `dict` | 렌더링 옵션 |

##### 예제

```python
import pandas as pd
import plotly.express as px

# 테이블 출력
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
instance.result("table", df)

# 차트 출력
fig = px.line(df, x='a', y='b')
instance.result("chart", fig)

# HTML 출력
html = "<h1>Complete</h1>"
instance.result("html", html)
```

---

#### `drive(*path)`

워크플로우 작업 디렉토리 기준의 스토리지 객체를 반환합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `*path` | `str` | 경로 세그먼트 |

##### 반환값

`Storage` - 스토리지 객체

##### 예제

```python
# 루트 디렉토리
fs = instance.drive()
fs.write("output.txt", "Hello")

# 하위 디렉토리
fs = instance.drive("data", "results")
fs.write("result.json", {"status": "ok"})

# 파일 읽기
content = fs.read("output.txt")
```

---

#### `binding(flask=None, path=None)`

웹 요청 바인딩 객체를 생성합니다 (API 앱용).

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `flask` | `Flask` | Flask 앱 객체 |
| `path` | `str` | 요청 경로 |

##### 반환값

`Binding` - 바인딩 객체

##### Binding 객체 속성

| 속성 | 타입 | 설명 |
|-----|------|------|
| `flow` | `Flow` | Flow 객체 |
| `input(name, default)` | `function` | 입력 조회 |
| `inputs(name)` | `function` | 다중 입력 조회 |
| `output(*args, **kwargs)` | `function` | 출력 설정/조회 |
| `result(name, value)` | `function` | 결과 출력 |
| `drive(*path)` | `function` | 스토리지 |
| `clear()` | `function` | 로그 삭제 |
| `request` | `Request` | 웹 요청 객체 (flask 제공 시) |
| `response` | `Response` | 웹 응답 객체 (flask 제공 시) |
| `run(flow, **kwargs)` | `function` | 워크플로우 실행 (flask 제공 시) |
| `stop()` | `function` | 워크플로우 중지 (flask 제공 시) |

##### 예제

```python
# API 코드에서 사용 (app.api 필드)
wiz = instance.binding(flask_app, request_path)

# 입력 조회
data = dizest.input("data", default=[])

# 출력 설정
dizest.output("result", processed_data)

# 웹 응답
dizest.response.json({"status": "ok"})
```

---

#### `run(threaded=True, **params)`

Flow를 실행합니다 (FlowInstance 내부에서).

##### 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `threaded` | `bool` | `True` | 백그라운드 실행 여부 |
| `**params` | `dict` | `{}` | 입력 파라미터 |

##### 예제

```python
# 현재 Flow에서 다른 Flow 실행
another_flow = workflow.flow("other_flow_id")
instance.run(another_flow, threaded=True, param1="value1")
```

---

## 사용 예제

### Flow 정보 확인

```python
workflow = dizest.Workflow("myworkflow.dwp")

for flow in workflow.flows():
    print(f"Flow: {flow.id()}")
    print(f"  Title: {flow.title()}")
    print(f"  Active: {flow.active()}")
    print(f"  App: {flow.app().title()}")
    print(f"  Inputs: {list(flow.inputs().keys())}")
    print(f"  Previous: {flow.previous()}")
    print()
```

### 실행 후 결과 확인

```python
workflow = dizest.Workflow("myworkflow.dwp")
workflow.run()

for flow in workflow.flows():
    instance = workflow.run.instance(flow)
    print(f"Flow: {flow.id()}")
    print(f"  Status: {instance.status()}")
    print(f"  Output: {instance.output_data}")
    print(f"  Logs: {instance.log()}")
    print()
```

### App 코드에서 사용 (wiz 객체)

App의 `code` 필드에서는 `wiz` 객체를 통해 FlowInstance 기능에 접근합니다:

```python
# 입력 받기
data = dizest.input("data", default=[])
message = dizest.input("message", default="Hello")

# 처리
result = [x * 2 for x in data]

# 출력
dizest.output("result", result)
dizest.output("count", len(result))

# 결과 시각화
import pandas as pd
df = pd.DataFrame(result, columns=['value'])
dizest.result("table", df)

# 로그
print(f"Processed {len(data)} items")

# 파일 저장
fs = dizest.drive()
fs.write("result.json", {"data": result})
```

---

## 관련 문서

- [Workflow 클래스 API](workflow.md)
- [Serve 클래스 API](serve.md)
- [사용 가이드](../usage-guide.md)
