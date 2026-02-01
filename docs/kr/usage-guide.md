# DIZEST 사용 가이드

## 목차

1. [설치](#설치)
2. [시작하기](#시작하기)
3. [워크플로우 생성](#워크플로우-생성)
4. [App 작성하기](#app-작성하기)
5. [Flow 연결하기](#flow-연결하기)
6. [워크플로우 실행](#워크플로우-실행)
7. [외부 API 호출](#외부-api-호출)
8. [고급 사용법](#고급-사용법)

---

## 설치

### 1. pip를 통한 설치

```bash
pip install dizest
```

### 2. 프로젝트 생성

```bash
dizest install myproject
```

프로젝트가 생성되면 자동으로 생성된 비밀번호가 출력됩니다:

```
dizest installed at `myproject`
password: aB3dE5fG7hI9jK1l
```

### 3. 커스텀 비밀번호로 설치

```bash
dizest install myproject --password mysecretpass
```

### 4. 소스코드로 설치 (개발자용)

```bash
cd <workspace>
wiz create dizest --uri https://github.com/season-framework/dizest-ui-angular
```

---

## 시작하기

### 서버 실행

#### 일반 모드

```bash
cd myproject
dizest run --port 4000 --host 0.0.0.0
```

**옵션:**
- `--port`: 웹 서버 포트 (기본값: 3000)
- `--host`: 웹 서버 호스트 (기본값: 0.0.0.0)
- `--log`: 로그 파일 경로 (기본값: None)

#### 데몬 모드

```bash
dizest server start  # 데몬 시작
dizest server stop   # 데몬 중지
```

### 웹 UI 접속

브라우저에서 다음 주소로 접속:

```
http://localhost:4000
```

로그인 정보:
- 사용자명: `root`
- 비밀번호: 설치 시 생성된 비밀번호

---

## 워크플로우 생성

### 1. 새 워크플로우 만들기

1. 웹 UI에서 **New Workflow** 버튼 클릭
2. 워크플로우 이름 입력 (예: `my_workflow.dwp`)
3. **Create** 클릭

### 2. 워크플로우 구조 이해하기

워크플로우는 다음 두 가지 주요 요소로 구성됩니다:

#### App (애플리케이션)
- 재사용 가능한 코드 블록
- Python 코드, HTML, JavaScript, CSS 포함
- 입력(Inputs)과 출력(Outputs) 정의

#### Flow (플로우)
- App의 인스턴스
- 캔버스에 배치되는 노드
- 다른 Flow와 연결 가능

---

## App 작성하기

### 1. 새 App 생성

좌측 사이드바에서 **Apps** 탭 클릭 → **+ 버튼** 클릭

### 2. App 기본 구조

```json
{
  "id": "unique_app_id",
  "title": "My App",
  "version": "1.0.0",
  "inputs": [
    {
      "type": "variable",
      "name": "message",
      "inputtype": "text"
    },
    {
      "type": "output",
      "name": "data"
    }
  ],
  "outputs": [
    {
      "name": "result"
    }
  ],
  "code": "# Python 코드"
}
```

### 3. 입력 타입

#### Variable (변수)

사용자가 직접 값을 입력:

```json
{
  "type": "variable",
  "name": "count",
  "inputtype": "number"
}
```

**inputtype 종류:**
- `text`: 텍스트 입력
- `number`: 숫자 입력
- `checkbox`: 체크박스 (boolean)
- `textarea`: 여러 줄 텍스트

#### Output (출력 연결)

다른 Flow의 출력과 연결:

```json
{
  "type": "output",
  "name": "input_data"
}
```

### 4. Python 코드 작성

App의 `code` 필드에 Python 코드를 작성합니다.

#### 기본 예제

```python
# 입력 받기
name = dizest.input("name", default="World")

# 출력 설정
result = f"Hello, {name}!"
dizest.output("greeting", result)

# 로그 출력
print(f"Processed: {name}")
```

#### 다른 Flow 출력 사용

```python
# 'data' 입력은 다른 Flow의 출력과 연결됨
input_data = dizest.input("data", default=[])

# 데이터 처리
processed = [x * 2 for x in input_data]

# 출력
dizest.output("result", processed)
```

#### 여러 입력 받기

```python
# 동일 입력에 연결된 모든 Flow의 출력
all_inputs = dizest.inputs("data")
# 결과: [data1, data2, data3, ...]

total = sum(all_inputs)
dizest.output("sum", total)
```

### 5. 결과 시각화

```python
import pandas as pd
import matplotlib.pyplot as plt

# 데이터 생성
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

# Plotly 차트
import plotly.express as px
fig = px.line(df, x='x', y='y')
dizest.result("chart", fig)

# 테이블
dizest.result("table", df)

# HTML
html_content = "<h1>결과</h1><p>완료되었습니다.</p>"
dizest.result("html", html_content)
```

### 6. 파일 저장 및 읽기

```python
# 워크플로우 디렉토리 기준 스토리지
fs = dizest.drive()

# 파일 쓰기
fs.write("output.txt", "Hello World")

# 파일 읽기
content = fs.read("output.txt")

# 하위 디렉토리
fs = dizest.drive("data", "results")
fs.write("result.json", {"status": "success"})
```

---

## Flow 연결하기

### 1. Flow 추가

1. 좌측 **Apps** 탭에서 원하는 App을 캔버스로 드래그
2. Flow가 생성됨

### 2. Flow 연결

#### 출력 → 입력 연결

1. 소스 Flow의 **출력 포인트** 클릭
2. 대상 Flow의 **입력 포인트**로 드래그
3. 선이 연결됨

#### 연결 예제

```
[Flow A] ---output---> [Flow B]
    |                      |
    └---data----------> [Flow C]
```

- Flow A의 `output`이 Flow B의 입력으로 전달
- Flow A의 `data`가 Flow C의 입력으로 전달

### 3. Flow 설정

Flow를 클릭하면 우측에 설정 패널이 나타납니다:

- **Title**: Flow 이름 (표시용)
- **Active**: 활성화 여부 (비활성 Flow는 실행되지 않음)
- **Variables**: 변수 타입 입력의 값 설정

---

## 워크플로우 실행

### 1. 웹 UI에서 실행

1. 상단 툴바의 **Run** 버튼 클릭
2. 실행 진행 상황을 실시간으로 확인
3. 각 Flow의 로그 및 결과 확인

### 2. Python 코드로 실행

```python
import dizest

# 워크플로우 로드
workflow = dizest.Workflow("myworkflow.dwp")

# 실행
workflow.run()

# 특정 Flow만 실행
flow = workflow.flow("flow_id")
workflow.run(flow)

# 파라미터 전달
workflow.run(flow, param1="value1", param2="value2")
```

### 3. 실행 흐름

DIZEST는 자동으로 실행 순서를 계산합니다:

1. **의존성 분석**: 어떤 Flow가 어떤 Flow의 출력을 필요로 하는지 파악
2. **순서 결정**: DAG(Directed Acyclic Graph) 기반으로 순서 결정
3. **병렬 실행**: 의존성이 없는 Flow들은 동시에 실행
4. **데이터 전달**: 앞선 Flow의 출력을 다음 Flow의 입력으로 전달

---

## 외부 API 호출

### 1. REST API를 통한 실행

```bash
curl "http://localhost:4000/dizest/api/run/myworkflow.dwp?param1=value1&param2=value2"
```

**응답:**
```json
{
  "output1": "result value",
  "output2": [1, 2, 3]
}
```

### 2. 스트리밍 API

실시간 로그를 받아보려면:

```bash
curl "http://localhost:4000/dizest/api/stream/myworkflow.dwp?param1=value1"
```

Server-Sent Events (SSE) 형식으로 실시간 로그가 전송됩니다.

### 3. Python에서 API 호출

```python
import requests

response = requests.get(
    "http://localhost:4000/dizest/api/run/myworkflow.dwp",
    params={"message": "Hello"}
)

result = response.json()
print(result)
```

---

## 고급 사용법

### 1. 이벤트 리스너

```python
import dizest

workflow = dizest.Workflow("myworkflow.dwp")

# 로그 이벤트
def on_log(flow_id, event_name, value):
    print(f"[{flow_id}] {value}")

workflow.on('log.append', on_log)

# 상태 변경 이벤트
def on_status(flow_id, event_name, value):
    print(f"Flow {flow_id} status: {value}")

workflow.on('flow.status', on_status)

workflow.run()
```

### 2. 커스텀 렌더러

```python
from dizest.core.renderer import Renderer

class MyRenderer(Renderer):
    def render(self, value, **kwargs):
        # 커스텀 렌더링 로직
        if isinstance(value, MyCustomType):
            return self.custom_format(value)
        return super().render(value, **kwargs)

# 워크플로우에 적용
workflow.render = MyRenderer()
```

### 3. Serve 클래스를 이용한 임베딩

```python
import dizest

# 서버 생성
serve = dizest.Serve(host='0.0.0.0', port=8000)

# 이벤트 리스너
serve.on('log.append', lambda flow_id, event, value: print(value))

# 서버 실행
serve.run()
```

### 4. 조건부 실행

Flow의 `active` 속성을 동적으로 변경:

```python
workflow = dizest.Workflow("myworkflow.dwp")

# 특정 Flow 비활성화
flow = workflow.flow("flow_id")
flow.update(active=False)

# 실행 (비활성 Flow는 건너뜀)
workflow.run()
```

### 5. 워크플로우 분석

```python
# 필요한 입력과 제공되는 출력 확인
requested, outputs = workflow.spec()

print("필요한 입력:", requested)
# {'flow_id': {'param1': None, 'param2': None}}

print("최종 출력:", outputs)
# {'flow_id': ['output1', 'output2']}
```

### 6. 로그 크기 제한

```python
workflow = dizest.Workflow(
    "myworkflow.dwp",
    max_log_size=100  # 최대 100개의 로그 항목 유지
)
```

### 7. 작업 디렉토리 설정

```python
workflow = dizest.Workflow(
    "myworkflow.dwp",
    cwd="/path/to/working/directory"
)
```

---

## 베스트 프랙티스

### 1. App 설계 원칙

- **단일 책임**: 각 App은 하나의 명확한 기능 수행
- **재사용성**: 다양한 워크플로우에서 사용할 수 있도록 일반화
- **문서화**: `description` 필드에 App의 용도 명시

### 2. 에러 처리

```python
try:
    # 작업 수행
    result = process_data(dizest.input("data"))
    dizest.output("result", result)
except Exception as e:
    # 에러 로그
    print(f"Error: {str(e)}")
    # 기본값 출력
    dizest.output("result", None)
```

### 3. 성능 최적화

- 큰 데이터는 파일로 저장하고 경로만 전달
- 중간 결과를 캐싱하여 재실행 시 활용
- 독립적인 작업은 별도 Flow로 분리하여 병렬 실행

### 4. 디버깅

```python
# 디버그 정보 출력
print(f"Input type: {type(dizest.input('data'))}")
print(f"Input value: {dizest.input('data')}")

# 중간 결과 확인
dizest.result("debug", intermediate_value)
```

---

## 다음 단계

- [API 레퍼런스](api/README.md)에서 상세한 API 문서 확인
- [DWP 파일 규격](dwp-specification.md)에서 워크플로우 파일 형식 이해
- [예제 모음](examples.md)에서 다양한 활용 사례 확인

---

## 문제 해결

### 워크플로우가 실행되지 않음

1. 모든 Flow의 `active` 속성이 `true`인지 확인
2. 순환 의존성이 없는지 확인
3. 필요한 입력이 모두 제공되었는지 확인

### 연결이 되지 않음

1. 출력 타입과 입력 타입이 일치하는지 확인
2. Flow가 활성 상태인지 확인

### 데이터가 전달되지 않음

1. 소스 Flow가 `dizest.output()`으로 데이터를 출력했는지 확인
2. 출력 이름과 입력 이름이 정확히 일치하는지 확인
3. 실행 순서가 올바른지 확인 (의존성 분석 결과 확인)
