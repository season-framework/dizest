# DIZEST 한국어 문서

![DIZEST Logo](../../screenshots/DIZEST_main.gif)

DIZEST(Data Intelligence Workflow Execution System & Tools)에 오신 것을 환영합니다.

## 소개

DIZEST는 웹 기술 기반의 로우코드 워크플로우 플랫폼으로, 인공지능 및 데이터 분석 작업을 시각적으로 구성하고 실행할 수 있도록 지원합니다.

### 주요 특징

- 🎨 **시각적 워크플로우 편집기**: 드래그 앤 드롭 방식의 직관적인 UI
- 🔄 **재사용 가능한 컴포넌트**: App을 한 번 만들고 여러 곳에서 사용
- ⚡ **병렬 실행**: 의존성이 없는 작업은 자동으로 병렬 실행
- 🐍 **Python 기반**: 익숙한 Python으로 로직 작성
- 🌐 **REST API 지원**: 워크플로우를 웹 API로 즉시 배포
- 📊 **다양한 시각화**: Matplotlib, Plotly, Pandas 등 지원
- 🔌 **확장 가능**: 플러그인 시스템을 통한 기능 확장

## 빠른 시작

### 설치

```bash
pip install dizest
dizest install myproject
cd myproject
dizest run --port 4000
```

브라우저에서 `http://localhost:4000` 접속

### 첫 워크플로우 만들기

1. **New Workflow** 버튼 클릭
2. 좌측 사이드바에서 **Apps** 탭 선택
3. **+ 버튼**으로 새 App 생성
4. Python 코드 작성:
   ```python
   message = dizest.input("message", default="Hello")
   result = message.upper()
   dizest.output("result", result)
   print(f"Processed: {result}")
   ```
5. App을 캔버스로 드래그하여 Flow 생성
6. **Run** 버튼으로 실행

## 문서 구조

### 📘 기본 가이드

- [아키텍처](architecture.md) - DIZEST의 전체 구조와 설계 원칙
- [사용 가이드](usage-guide.md) - 설치부터 고급 사용법까지
- [DWP 파일 규격](dwp-specification.md) - 워크플로우 파일 형식

### 📗 API 레퍼런스

- [Workflow 클래스](api/workflow.md) - 워크플로우 관리 및 실행
- [Flow, App, FlowInstance 클래스](api/flow-app-instance.md) - 워크플로우 구성 요소
- [Serve 클래스](api/serve.md) - 웹 서버 및 REST API
- [CLI 명령어](api/cli.md) - 명령줄 인터페이스

### 📙 예제 및 활용

- [예제 모음](examples.md) - 다양한 활용 사례
- [사용 사례](../../USE_CASES.md) - 실제 프로젝트 적용 사례

## 주요 개념

### App (애플리케이션)

재사용 가능한 기능 단위입니다. Python 코드, HTML, JavaScript, CSS를 포함할 수 있습니다.

```python
# App 코드 예제
data = dizest.input("data", default=[])
processed = [x * 2 for x in data]
dizest.output("result", processed)
```

### Flow (플로우)

App의 인스턴스로, 캔버스에 배치되는 노드입니다. 여러 Flow를 연결하여 워크플로우를 구성합니다.

### Workflow (워크플로우)

여러 App과 Flow의 조합으로 구성된 완전한 작업 흐름입니다. `.dwp` 파일로 저장됩니다.

## 사용 예제

### Python 스크립트에서 실행

```python
import dizest

# 워크플로우 로드
workflow = dizest.Workflow("myworkflow.dwp")

# 이벤트 리스너
workflow.on('log.append', lambda f, e, log: print(log))

# 실행
workflow.run()
```

### REST API로 실행

```bash
curl "http://localhost:4000/dizest/api/run/myworkflow.dwp?param1=value1"
```

### 커스텀 서버

```python
from dizest import Serve

serve = Serve(host='0.0.0.0', port=8000)

@serve.app.route('/custom')
def custom():
    return {'status': 'ok'}

serve.run()
```

## 실제 활용 사례

### 데이터 분석 파이프라인

```
[데이터 로드] → [전처리] → [분석] → [시각화] → [보고서 생성]
```

### 머신러닝 워크플로우

```
[데이터 수집] → [피처 엔지니어링] → [모델 학습] → [평가] → [배포]
```

### 웹 크롤링 및 처리

```
[크롤링] → [파싱] → [정제] → [저장] → [알림]
```

## 시스템 요구사항

- **Python**: 3.7 이상
- **OS**: Linux, macOS, Windows
- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전)
- **메모리**: 최소 2GB RAM 권장
- **디스크**: 프로젝트당 약 100MB

## 설치 옵션

### pip를 통한 기본 설치

```bash
pip install dizest
```

### 개발 버전 설치

```bash
pip install git+https://github.com/season-framework/dizest.git
```

### Docker 사용

```bash
docker pull seasonframework/dizest
docker run -p 4000:4000 seasonframework/dizest
```

## 커뮤니티 및 지원

- **GitHub**: [https://github.com/season-framework/dizest](https://github.com/season-framework/dizest)
- **이슈 트래커**: [GitHub Issues](https://github.com/season-framework/dizest/issues)
- **이메일**: proin@season.co.kr
- **라이선스**: MIT License

## 기여하기

DIZEST는 오픈소스 프로젝트입니다. 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 버전 히스토리

- **v2.4**: 최신 안정 버전
- **v2.3**: 성능 개선 및 버그 수정
- **v2.2**: 새로운 렌더러 추가
- **v2.1**: API 개선
- **v2.0**: 주요 아키텍처 업데이트

자세한 변경 사항은 [RELEASES.md](../../RELEASES.md)를 참조하세요.

## FAQ

### Q: DIZEST와 Apache Airflow의 차이점은?

A: DIZEST는 시각적 워크플로우 편집과 즉각적인 실행에 초점을 맞춘 로우코드 플랫폼입니다. Airflow는 스케줄링과 모니터링에 강점이 있는 반면, DIZEST는 빠른 프로토타이핑과 대화형 실행에 적합합니다.

### Q: 상용 프로젝트에 사용할 수 있나요?

A: 네, MIT 라이선스하에 상용 프로젝트에 자유롭게 사용할 수 있습니다.

### Q: 대용량 데이터 처리가 가능한가요?

A: DIZEST는 Python 기반이므로 Pandas, Dask, PySpark 등의 라이브러리를 활용하여 대용량 데이터를 처리할 수 있습니다.

### Q: 클라우드 배포가 가능한가요?

A: 네, Docker를 통해 AWS, GCP, Azure 등 모든 클라우드 플랫폼에 배포할 수 있습니다.

## 라이선스

```
MIT License

Copyright (c) 2021 SEASON CO. LTD.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**DIZEST로 워크플로우를 더 쉽고 빠르게 구축하세요!** 🚀
