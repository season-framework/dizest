# Serve 클래스 API 레퍼런스

## 개요

`Serve` 클래스는 DIZEST 워크플로우를 Flask 웹 서버에 임베딩하여 REST API로 제공하는 기능을 담당합니다.

## 클래스 정의

```python
from dizest import Serve

serve = Serve(**config)
```

## 생성자

### `__init__(**config)`

Serve 객체를 생성하고 Flask 앱을 초기화합니다.

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `cwd` | `str` | ✗ | `os.getcwd()` | 워크플로우 작업 디렉토리 |
| `max_log_size` | `int` | ✗ | `50` | 최대 로그 항목 수 |
| `host` | `str` | ✗ | `127.0.0.1` | 웹 서버 호스트 주소 |
| `port` | `int` | ✗ | `8000` | 웹 서버 포트 |

#### 예제

```python
# 기본 설정
serve = Serve()

# 커스텀 설정
serve = Serve(
    host='0.0.0.0',
    port=5000,
    cwd='/path/to/workdir',
    max_log_size=100
)
```

---

## 속성

### `config`

서버 설정 객체입니다.

**타입**: `Config`

**속성**:
- `cwd`: 작업 디렉토리
- `max_log_size`: 최대 로그 크기
- `host`: 서버 호스트
- `port`: 서버 포트

### `workflow`

내부 워크플로우 객체입니다.

**타입**: `Workflow`

### `app`

Flask 앱 인스턴스입니다.

**타입**: `flask.Flask`

### `flask`

Flask 모듈 참조입니다.

**타입**: `module`

---

## 메서드

### 서버 제어

#### `run()`

웹 서버를 시작합니다 (블로킹).

##### 예제

```python
serve = Serve(host='0.0.0.0', port=8000)
serve.run()  # 서버 시작 (Ctrl+C로 종료)
```

---

### 이벤트 처리

#### `on(name, fn)`

워크플로우 이벤트 리스너를 등록합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `name` | `str` | 이벤트 이름 |
| `fn` | `callable` | 이벤트 핸들러 함수 |

##### 이벤트 타입

- `workflow.status`: 워크플로우 상태 변경
- `flow.status`: Flow 상태 변경
- `flow.index`: Flow 실행 순서
- `log.append`: 로그 추가
- `log.clear`: 로그 삭제
- `result`: 결과 출력

##### 예제

```python
serve = Serve()

def on_log(flow_id, event_name, log_message):
    print(f"[{flow_id}] {log_message}")

serve.on('log.append', on_log)

serve.run()
```

---

### 요청 처리

#### `query(key=None, default=None)`

현재 요청의 쿼리 파라미터를 조회합니다.

##### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `key` | `str` 또는 `None` | 조회할 파라미터 이름 (None이면 전체) |
| `default` | `any` | 기본값 |

##### 반환값

- `key=None`: 전체 쿼리 파라미터 딕셔너리
- `key` 지정: 해당 파라미터 값 (없으면 `default`)

##### 예제

```python
from dizest import Serve

serve = Serve()

@serve.app.route('/api/test')
def test():
    # 전체 파라미터
    all_params = serve.query()
    
    # 특정 파라미터
    message = serve.query('message', default='Hello')
    count = serve.query('count', default=0)
    
    return {'message': message, 'count': count}

serve.run()
```

---

## 기본 제공 API 엔드포인트

Serve 클래스는 다음 REST API 엔드포인트를 자동으로 바인딩합니다:

### Health Check

**엔드포인트**: `GET /health`

서버 상태를 확인합니다.

**응답**:
```json
{
  "code": 200
}
```

**예제**:
```bash
curl http://localhost:8000/health
```

---

### Workflow API

#### Update Workflow

**엔드포인트**: `POST /workflow/update`

워크플로우를 업데이트합니다.

**파라미터**:
- `package` (JSON string): 워크플로우 패키지

**응답**:
```json
{
  "code": 200,
  "data": { /* sync data */ }
}
```

**예제**:
```bash
curl -X POST http://localhost:8000/workflow/update \
  -d 'package={"apps":{...},"flow":{...}}'
```

---

#### Get Workflow Status

**엔드포인트**: `GET /workflow/status`

워크플로우 실행 상태를 조회합니다.

**응답**:
```json
{
  "code": 200,
  "status": "idle"
}
```

**예제**:
```bash
curl http://localhost:8000/workflow/status
```

---

#### Run Workflow

**엔드포인트**: `POST /workflow/run`

워크플로우를 실행합니다.

**응답**:
```json
{
  "code": 200,
  "status": "start"
}
```

**예제**:
```bash
curl -X POST http://localhost:8000/workflow/run
```

---

#### Stop Workflow

**엔드포인트**: `POST /workflow/stop`

실행 중인 워크플로우를 중지합니다.

**응답**:
```json
{
  "code": 200
}
```

**예제**:
```bash
curl -X POST http://localhost:8000/workflow/stop
```

---

### Flow API

#### Get Flow Status

**엔드포인트**: `GET /flow/status/<flow_id>`

특정 Flow의 상태를 조회합니다.

**응답**:
```json
{
  "code": 200,
  "status": "idle",
  "index": -1,
  "log": []
}
```

**예제**:
```bash
curl http://localhost:8000/flow/status/my_flow-1234567890
```

---

#### Run Flow

**엔드포인트**: `POST /flow/run/<flow_id>`

특정 Flow를 실행합니다.

**파라미터**: URL 쿼리 파라미터로 입력 전달

**응답**:
```json
{
  "code": 200,
  "status": "start"
}
```

**예제**:
```bash
curl -X POST "http://localhost:8000/flow/run/my_flow-1234567890?param1=value1&param2=value2"
```

---

## 커스텀 엔드포인트 추가

### 방법 1: Flask 데코레이터 사용

```python
from dizest import Serve

serve = Serve()

@serve.app.route('/custom/api')
def custom_api():
    # 쿼리 파라미터 받기
    message = serve.query('message', default='Hello')
    
    # 워크플로우 로드 및 실행
    workflow = serve.workflow
    workflow.load('myworkflow.dwp')
    workflow.run()
    
    # 결과 반환
    return {'status': 'success', 'message': message}

serve.run()
```

### 방법 2: 바인딩 클래스 작성

```python
from dizest.base.binding import BaseBinding

class CustomBinding(BaseBinding):
    NAMESPACE = "custom"
    
    def hello(self):
        name = self.serve.query('name', default='World')
        return {'code': 200, 'message': f'Hello, {name}!'}
    
    def process(self):
        data = self.serve.query('data')
        # 데이터 처리 로직
        result = process_data(data)
        return {'code': 200, 'result': result}

# Serve 클래스 확장
from dizest import Serve

class MyServe(Serve):
    def bind(self):
        super().bind()
        CustomBinding(self).bind()

serve = MyServe()
serve.run()
```

이제 다음 엔드포인트를 사용할 수 있습니다:
- `GET /custom/hello?name=John`
- `POST /custom/process?data=...`

---

## 전체 사용 예제

### 기본 서버

```python
from dizest import Serve

# 서버 생성
serve = Serve(host='0.0.0.0', port=8000)

# 이벤트 리스너
def on_log(flow_id, event, value):
    print(f"[{flow_id}] {value}")

serve.on('log.append', on_log)

# 서버 실행
serve.run()
```

### 커스텀 API가 있는 서버

```python
from dizest import Serve
import dizest

serve = Serve(host='0.0.0.0', port=5000)

@serve.app.route('/api/run/<workflow_name>')
def run_workflow(workflow_name):
    # 워크플로우 로드
    workflow_path = f'/workflows/{workflow_name}.dwp'
    workflow = dizest.Workflow(workflow_path)
    
    # 파라미터 수집
    params = serve.query()
    
    # 실행
    workflow.run(**params)
    
    # 결과 수집
    requested, outputs = workflow.spec()
    result = {}
    
    for flow_id in outputs:
        flow = workflow.flow(flow_id)
        instance = workflow.run.instance(flow)
        for output_name in outputs[flow_id]:
            result[output_name] = instance.output_data.get(output_name)
    
    return {'status': 'success', 'result': result}

serve.run()
```

### 인증이 있는 서버

```python
from dizest import Serve
from functools import wraps

serve = Serve()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = serve.query('token')
        if token != 'secret-token':
            return {'code': 401, 'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated

@serve.app.route('/api/secure')
@require_auth
def secure_api():
    return {'code': 200, 'data': 'Secure data'}

serve.run()
```

---

## 프로덕션 배포

### uWSGI로 배포

```python
# app.py
from dizest import Serve

serve = Serve()

# uWSGI 앱 객체
app = serve.app

if __name__ == '__main__':
    serve.run()
```

**uWSGI 설정** (`uwsgi.ini`):
```ini
[uwsgi]
module = app:app
master = true
processes = 4
threads = 2
socket = 0.0.0.0:8000
chmod-socket = 660
vacuum = true
die-on-term = true
```

**실행**:
```bash
uwsgi --ini uwsgi.ini
```

### Gunicorn으로 배포

```python
# app.py
from dizest import Serve

serve = Serve()
app = serve.app
```

**실행**:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker로 배포

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

---

## 에러 처리

Serve 클래스는 모든 예외를 자동으로 처리하여 JSON 응답으로 반환합니다:

```python
@serve.app.errorhandler(Exception)
def handle_exception(e):
    return {"code": 500, "data": str(e)}
```

커스텀 에러 핸들러를 추가할 수 있습니다:

```python
@serve.app.errorhandler(404)
def not_found(e):
    return {"code": 404, "error": "Not Found"}, 404

@serve.app.errorhandler(ValueError)
def value_error(e):
    return {"code": 400, "error": str(e)}, 400
```

---

## 보안 고려사항

### CORS 설정

```python
from flask_cors import CORS

serve = Serve()
CORS(serve.app)
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

serve = Serve()
limiter = Limiter(
    serve.app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@serve.app.route('/api/limited')
@limiter.limit("10 per minute")
def limited():
    return {'status': 'ok'}
```

---

## 관련 문서

- [Workflow API](workflow.md)
- [CLI API](cli.md)
- [사용 가이드](../usage-guide.md)
