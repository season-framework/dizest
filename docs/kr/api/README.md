# API 레퍼런스

DIZEST의 주요 클래스 및 인터페이스에 대한 상세한 API 문서입니다.

## 주요 클래스

### [Workflow 클래스](workflow.md)

워크플로우를 로드하고 관리하며 실행하는 핵심 클래스입니다.

**주요 메서드:**
- `__init__(package, **kwargs)` - 워크플로우 생성
- `load(package)` - 워크플로우 로드
- `apps()` - App 목록 조회
- `app(app_id)` - 특정 App 조회
- `flows()` - Flow 목록 조회
- `flow(flow_id)` - 특정 Flow 조회
- `on(name, fn)` - 이벤트 리스너 등록
- `spec()` - 워크플로우 입출력 분석
- `run(flow, **kwargs)` - 워크플로우 실행

**사용 예제:**
```python
import dizest

workflow = dizest.Workflow("myworkflow.dwp")
workflow.on('log.append', lambda f, e, log: print(log))
workflow.run()
```

---

### [Flow, App, FlowInstance 클래스](flow-app-instance.md)

워크플로우를 구성하는 핵심 컴포넌트들입니다.

#### Flow 클래스

캔버스에 배치된 App의 인스턴스입니다.

**주요 메서드:**
- `id()` - Flow ID 조회
- `title()` - Flow 제목 조회
- `active()` - 활성화 상태 확인
- `app()` - 참조하는 App 조회
- `inputs()` - 입력 정보 조회
- `previous()` - 이전 Flow 목록
- `update(**kwargs)` - Flow 속성 업데이트

#### App 클래스

재사용 가능한 코드 블록입니다.

**주요 메서드:**
- `id()` - App ID 조회
- `title()` - App 제목 조회
- `code()` - Python 코드 조회
- `inputs()` - 입력 정의 조회
- `outputs()` - 출력 정의 조회
- `update(**kwargs)` - App 속성 업데이트

#### FlowInstance 클래스

실행 중인 Flow의 상태를 관리합니다.

**주요 메서드:**
- `status(value)` - 상태 조회/설정
- `log(value)` - 로그 조회/추가
- `input(name, default)` - 입력 조회
- `inputs(name)` - 다중 입력 조회
- `output(*args, **kwargs)` - 출력 설정/조회
- `result(name, value)` - 결과 렌더링
- `drive(*path)` - 파일 스토리지
- `clear()` - 로그 삭제

**사용 예제 (App 코드 내부):**
```python
# 입력 받기
data = dizest.input("data", default=[])
message = dizest.input("message", default="Hello")

# 처리
result = [x * 2 for x in data]

# 출력
dizest.output("result", result)
print(f"Processed {len(result)} items")

# 파일 저장
fs = dizest.drive()
fs.write("output.json", {"result": result})
```

---

### [Serve 클래스](serve.md)

DIZEST를 Flask 웹 서버로 실행하고 REST API를 제공합니다.

**주요 메서드:**
- `__init__(**config)` - 서버 생성
- `run()` - 서버 시작
- `on(name, fn)` - 이벤트 리스너 등록
- `query(key, default)` - 쿼리 파라미터 조회

**기본 API 엔드포인트:**
- `GET /health` - 헬스 체크
- `POST /workflow/update` - 워크플로우 업데이트
- `GET /workflow/status` - 워크플로우 상태
- `POST /workflow/run` - 워크플로우 실행
- `POST /workflow/stop` - 워크플로우 중지
- `GET /flow/status/<flow_id>` - Flow 상태
- `POST /flow/run/<flow_id>` - Flow 실행

**사용 예제:**
```python
from dizest import Serve

serve = Serve(host='0.0.0.0', port=8000)

@serve.app.route('/custom')
def custom_api():
    param = serve.query('param', default='default')
    return {'status': 'ok', 'param': param}

serve.run()
```

---

### [CLI 명령어](cli.md)

DIZEST 명령줄 인터페이스입니다.

**프로젝트 관리:**
- `dizest install [PROJECT_NAME]` - 프로젝트 생성
- `dizest upgrade` - 프로젝트 업그레이드
- `dizest password <PASSWORD>` - 비밀번호 변경

**서버 실행:**
- `dizest run` - 서버 실행 (포그라운드)
- `dizest server start` - 서버 시작 (데몬)
- `dizest server stop` - 서버 중지
- `dizest kill` - 모든 서버 프로세스 종료

**서비스 관리:**
- `dizest service install` - systemd 서비스 등록
- `dizest service start` - 서비스 시작
- `dizest service stop` - 서비스 중지
- `dizest service status` - 서비스 상태 확인

---

## 데이터 타입 및 구조

### 워크플로우 패키지 구조

```python
{
    "apps": {
        "app_id": {
            "id": str,
            "title": str,
            "version": str,
            "inputs": list,
            "outputs": list,
            "code": str,
            ...
        }
    },
    "flow": {
        "flow_id": {
            "id": str,
            "app_id": str,
            "active": bool,
            "inputs": dict,
            "outputs": dict,
            "data": dict,
            "pos_x": int,
            "pos_y": int,
            ...
        }
    },
    ...
}
```

### 이벤트 타입

| 이벤트 | 파라미터 | 설명 |
|-------|---------|------|
| `workflow.status` | `(flow_id, event_name, status)` | 워크플로우 상태 변경 |
| `flow.status` | `(flow_id, event_name, status)` | Flow 상태 변경 |
| `flow.index` | `(flow_id, event_name, index)` | Flow 실행 순서 |
| `log.append` | `(flow_id, event_name, log)` | 로그 추가 |
| `log.clear` | `(flow_id, event_name, value)` | 로그 삭제 |
| `result` | `(flow_id, event_name, result)` | 결과 출력 |

### Flow 상태 값

- `idle` - 대기 중
- `pending` - 준비 중
- `running` - 실행 중
- `ready` - 완료
- `error` - 오류 발생

---

## 빠른 참조

### Workflow 실행

```python
import dizest

# 로드
workflow = dizest.Workflow("workflow.dwp")

# 이벤트
workflow.on('log.append', handler)

# 실행
workflow.run()

# 결과
requested, outputs = workflow.spec()
for flow_id in outputs:
    flow = workflow.flow(flow_id)
    instance = workflow.run.instance(flow)
    print(instance.output_data)
```

### App 코드 작성

```python
# 입력
data = dizest.input("data", default=[])
param = dizest.input("param", default=1)

# 처리
result = process(data, param)

# 출력
dizest.output("result", result)

# 로그
print(f"Processed {len(data)} items")

# 결과 시각화
import pandas as pd
df = pd.DataFrame(result)
dizest.result("table", df)

# 파일 저장
fs = dizest.drive()
fs.write("output.json", result)
```

### REST API 호출

```bash
# 워크플로우 실행
curl "http://localhost:4000/dizest/api/run/workflow.dwp?param1=value1"

# 스트리밍 실행
curl "http://localhost:4000/dizest/api/stream/workflow.dwp?param1=value1"
```

---

## 관련 문서

- [사용 가이드](../usage-guide.md) - 전체 사용법
- [아키텍처](../architecture.md) - 시스템 구조
- [DWP 파일 규격](../dwp-specification.md) - 파일 형식
- [예제 모음](../examples.md) - 활용 사례
