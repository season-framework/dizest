# DWP 파일 규격 가이드

## 개요

DWP(DIZEST Workflow Package) 파일은 DIZEST 워크플로우를 저장하는 JSON 형식의 파일입니다. 확장자는 `.dwp`를 사용합니다.

## 파일 구조

### 최상위 구조

```json
{
  "apps": {},
  "flow": {},
  "title": "",
  "description": "",
  "version": "",
  "visibility": "",
  "category": "",
  "featured": "",
  "logo": "",
  "id": "",
  "kernel_id": "",
  "executable": null,
  "executable_name": "",
  "extra": {},
  "favorite": ""
}
```

### 필수 필드

| 필드 | 타입 | 설명 |
|-----|------|------|
| `apps` | object | App 정의 딕셔너리 |
| `flow` | object | Flow 인스턴스 딕셔너리 |

### 선택 필드

| 필드 | 타입 | 기본값 | 설명 |
|-----|------|--------|------|
| `title` | string | `""` | 워크플로우 제목 |
| `description` | string | `""` | 워크플로우 설명 |
| `version` | string | `""` | 버전 정보 |
| `visibility` | string | `"private"` | 공개 범위 (`public`, `private`) |
| `category` | string | `""` | 카테고리 |
| `featured` | string | `""` | 추천 워크플로우 여부 |
| `logo` | string | `""` | 로고 이미지 URL |
| `id` | string | `""` | 워크플로우 고유 ID |
| `kernel_id` | string | `""` | 실행 커널 ID |
| `executable` | string/null | `null` | 실행 파일 경로 |
| `executable_name` | string | `"base"` | 실행 환경 이름 |
| `extra` | object | `{}` | 추가 메타데이터 |
| `favorite` | string | `"0"` | 즐겨찾기 여부 |

---

## Apps 객체

`apps` 객체는 재사용 가능한 App들의 정의를 담고 있습니다.

### 구조

```json
{
  "apps": {
    "app_id_1": { /* App 정의 */ },
    "app_id_2": { /* App 정의 */ },
    ...
  }
}
```

### App 정의

```json
{
  "id": "unique_app_id",
  "title": "App Title",
  "version": "1.0.0",
  "description": "App description",
  "cdn": {
    "js": [],
    "css": []
  },
  "inputs": [],
  "outputs": [],
  "code": "",
  "api": "",
  "html": "",
  "js": "",
  "css": ""
}
```

### App 필드 상세

| 필드 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `id` | string | ✓ | App 고유 식별자 |
| `title` | string | ✓ | App 표시 이름 |
| `version` | string | ✗ | App 버전 |
| `description` | string | ✗ | App 설명 |
| `cdn` | object | ✗ | 외부 라이브러리 CDN |
| `cdn.js` | array | ✗ | JavaScript 라이브러리 URL 목록 |
| `cdn.css` | array | ✗ | CSS 라이브러리 URL 목록 |
| `inputs` | array | ✓ | 입력 정의 배열 |
| `outputs` | array | ✓ | 출력 정의 배열 |
| `code` | string | ✗ | Python 실행 코드 |
| `api` | string | ✗ | REST API 코드 |
| `html` | string | ✗ | HTML 템플릿 |
| `js` | string | ✗ | JavaScript 코드 |
| `css` | string | ✗ | CSS 스타일 |

### 입력 정의 (inputs)

```json
{
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
  ]
}
```

#### 입력 필드

| 필드 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `type` | string | ✓ | 입력 타입 (`variable` 또는 `output`) |
| `name` | string | ✓ | 입력 이름 (Python 변수명으로 사용) |
| `inputtype` | string | ✗ | 입력 필드 타입 (variable 타입인 경우) |

#### inputtype 값

| 값 | 설명 |
|----|------|
| `text` | 텍스트 입력 |
| `number` | 숫자 입력 |
| `textarea` | 여러 줄 텍스트 |
| `checkbox` | 체크박스 (boolean) |
| `select` | 드롭다운 선택 |

### 출력 정의 (outputs)

```json
{
  "outputs": [
    {
      "name": "result"
    },
    {
      "name": "summary"
    }
  ]
}
```

#### 출력 필드

| 필드 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `name` | string | ✓ | 출력 이름 |

---

## Flow 객체

`flow` 객체는 캔버스에 배치된 App 인스턴스들을 정의합니다.

### 구조

```json
{
  "flow": {
    "flow_id_1": { /* Flow 정의 */ },
    "flow_id_2": { /* Flow 정의 */ },
    ...
  }
}
```

### Flow 정의

```json
{
  "id": "app_id-1234567890",
  "app_id": "app_id",
  "active": true,
  "title": "",
  "description": "",
  "class": "",
  "name": "",
  "typenode": false,
  "pos_x": 100,
  "pos_y": 200,
  "height": 152,
  "data": {},
  "inputs": {},
  "outputs": {}
}
```

### Flow 필드 상세

| 필드 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `id` | string | ✓ | Flow 고유 ID (형식: `app_id-timestamp`) |
| `app_id` | string | ✓ | 참조하는 App의 ID |
| `active` | boolean | ✓ | 활성화 여부 |
| `title` | string | ✗ | Flow 제목 (없으면 App 제목 사용) |
| `description` | string | ✗ | Flow 설명 |
| `class` | string | ✗ | CSS 클래스 |
| `name` | string | ✗ | Flow 이름 |
| `typenode` | boolean | ✗ | 타입 노드 여부 |
| `pos_x` | number | ✓ | 캔버스 상의 X 좌표 |
| `pos_y` | number | ✓ | 캔버스 상의 Y 좌표 |
| `height` | number | ✗ | 노드 높이 |
| `data` | object | ✓ | 변수 입력 값 저장 |
| `inputs` | object | ✓ | 입력 연결 정보 |
| `outputs` | object | ✓ | 출력 연결 정보 |

### data 객체

변수 타입 입력의 값을 저장합니다.

```json
{
  "data": {
    "message": "Hello World",
    "count": "10",
    "enabled": true
  }
}
```

### inputs 객체

다른 Flow의 출력과의 연결을 정의합니다.

```json
{
  "inputs": {
    "data": {
      "connections": [
        {
          "node": "source_flow_id",
          "input": "output_name"
        }
      ]
    }
  }
}
```

#### 입력 연결 필드

| 필드 | 타입 | 설명 |
|-----|------|------|
| `connections` | array | 연결 배열 |
| `connections[].node` | string | 소스 Flow ID |
| `connections[].input` | string | 소스 Flow의 출력 이름 |

### outputs 객체

다른 Flow로의 출력 연결을 정의합니다.

```json
{
  "outputs": {
    "result": {
      "connections": [
        {
          "node": "target_flow_id",
          "output": "input_name"
        }
      ]
    }
  }
}
```

#### 출력 연결 필드

| 필드 | 타입 | 설명 |
|-----|------|------|
| `connections` | array | 연결 배열 |
| `connections[].node` | string | 대상 Flow ID |
| `connections[].output` | string | 대상 Flow의 입력 이름 |

---

## 완전한 예제

### 간단한 워크플로우

```json
{
  "title": "Simple Workflow",
  "description": "A simple data processing workflow",
  "version": "1.0.0",
  "visibility": "private",
  "category": "data-processing",
  "apps": {
    "data_loader": {
      "id": "data_loader",
      "title": "Data Loader",
      "version": "1.0.0",
      "description": "Load data from file",
      "cdn": {
        "js": [],
        "css": []
      },
      "inputs": [
        {
          "type": "variable",
          "name": "filepath",
          "inputtype": "text"
        }
      ],
      "outputs": [
        {
          "name": "data"
        }
      ],
      "code": "import json\nwith open(filepath) as f:\n    data = json.load(f)\ndizest.output('data', data)",
      "api": "",
      "html": "",
      "js": "",
      "css": ""
    },
    "data_processor": {
      "id": "data_processor",
      "title": "Data Processor",
      "version": "1.0.0",
      "description": "Process data",
      "cdn": {
        "js": [],
        "css": []
      },
      "inputs": [
        {
          "type": "output",
          "name": "input_data"
        },
        {
          "type": "variable",
          "name": "multiplier",
          "inputtype": "number"
        }
      ],
      "outputs": [
        {
          "name": "result"
        }
      ],
      "code": "data = dizest.input('input_data', [])\nmult = dizest.input('multiplier', 1)\nresult = [x * mult for x in data]\ndizest.output('result', result)\nprint(f'Processed {len(result)} items')",
      "api": "",
      "html": "",
      "js": "",
      "css": ""
    }
  },
  "flow": {
    "data_loader-1706123456789": {
      "id": "data_loader-1706123456789",
      "app_id": "data_loader",
      "active": true,
      "title": "",
      "description": "",
      "class": "",
      "name": "",
      "typenode": false,
      "pos_x": 100,
      "pos_y": 100,
      "height": 152,
      "data": {
        "filepath": "data.json"
      },
      "inputs": {},
      "outputs": {
        "data": {
          "connections": [
            {
              "node": "data_processor-1706123456790",
              "output": "input_data"
            }
          ]
        }
      }
    },
    "data_processor-1706123456790": {
      "id": "data_processor-1706123456790",
      "app_id": "data_processor",
      "active": true,
      "title": "",
      "description": "",
      "class": "",
      "name": "",
      "typenode": false,
      "pos_x": 400,
      "pos_y": 100,
      "height": 152,
      "data": {
        "multiplier": "2"
      },
      "inputs": {
        "input_data": {
          "connections": [
            {
              "node": "data_loader-1706123456789",
              "input": "data"
            }
          ]
        }
      },
      "outputs": {
        "result": {
          "connections": []
        }
      }
    }
  },
  "id": "simple_workflow.dwp",
  "kernel_id": "root-f07b4cf6-fbf3-11f0-b01a-3a26b58698d4",
  "executable": null,
  "executable_name": "base",
  "extra": {},
  "favorite": "0"
}
```

---

## 검증 규칙

### 필수 검증

1. **최상위 구조**
   - `apps` 객체 존재
   - `flow` 객체 존재

2. **App 정의**
   - 각 App은 고유한 `id` 보유
   - `title` 필드 존재
   - `inputs`, `outputs` 배열 존재

3. **Flow 정의**
   - 각 Flow는 고유한 `id` 보유
   - `app_id`가 `apps` 객체에 존재하는 App을 참조
   - `active`, `pos_x`, `pos_y` 필드 존재

### 연결 검증

1. **입력 연결**
   - `inputs`의 각 키는 App의 `inputs`에 정의된 이름과 일치
   - `connections[].node`는 존재하는 Flow ID 참조
   - `connections[].input`은 소스 Flow의 출력 이름과 일치

2. **출력 연결**
   - `outputs`의 각 키는 App의 `outputs`에 정의된 이름과 일치
   - `connections[].node`는 존재하는 Flow ID 참조
   - `connections[].output`은 대상 Flow의 입력 이름과 일치

### 순환 의존성 검증

- Flow 간 연결이 순환 구조를 형성하지 않아야 함
- DAG(Directed Acyclic Graph) 구조 유지

---

## 파일 생성 및 수정

### Python으로 DWP 생성

```python
import json

workflow = {
    "apps": {
        "my_app": {
            "id": "my_app",
            "title": "My App",
            "version": "1.0.0",
            "description": "",
            "cdn": {"js": [], "css": []},
            "inputs": [
                {"type": "variable", "name": "input1", "inputtype": "text"}
            ],
            "outputs": [
                {"name": "output1"}
            ],
            "code": "output1 = input1.upper()\ndizest.output('output1', output1)",
            "api": "",
            "html": "",
            "js": "",
            "css": ""
        }
    },
    "flow": {
        "my_app-1234567890": {
            "id": "my_app-1234567890",
            "app_id": "my_app",
            "active": True,
            "title": "",
            "description": "",
            "class": "",
            "name": "",
            "typenode": False,
            "pos_x": 100,
            "pos_y": 100,
            "height": 152,
            "data": {"input1": "hello"},
            "inputs": {},
            "outputs": {"output1": {"connections": []}}
        }
    },
    "title": "My Workflow",
    "description": "",
    "version": "1.0.0",
    "visibility": "private",
    "category": "",
    "id": "myworkflow.dwp"
}

with open("myworkflow.dwp", "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)
```

### 기존 DWP 수정

```python
import json
import dizest

# 로드
workflow = dizest.Workflow("myworkflow.dwp")

# Flow 추가
# (웹 UI에서 수행하는 것이 권장됨)

# 딕셔너리로 저장
package = workflow.to_dict()

with open("modified.dwp", "w", encoding="utf-8") as f:
    json.dump(package, f, indent=2, ensure_ascii=False)
```

---

## 베스트 프랙티스

### 1. ID 명명 규칙

- **App ID**: 소문자와 언더스코어 사용 (예: `data_loader`, `ml_model`)
- **Flow ID**: `{app_id}-{timestamp}` 형식 (예: `data_loader-1706123456789`)

### 2. 버전 관리

- 워크플로우 변경 시 `version` 필드 업데이트
- 시맨틱 버저닝 사용 권장 (예: `1.0.0`, `1.1.0`, `2.0.0`)

### 3. 문서화

- `description` 필드에 워크플로우 목적 명시
- 각 App의 `description`에 기능 설명 작성

### 4. 파일 관리

- 워크플로우 파일은 버전 관리 시스템(Git)에 포함
- 민감한 정보(비밀번호 등)는 환경 변수로 관리

---

## 관련 문서

- [사용 가이드](../usage-guide.md)
- [Workflow API](workflow.md)
- [아키텍처](../architecture.md)
