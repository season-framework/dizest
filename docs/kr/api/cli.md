# CLI API 레퍼런스

## 개요

DIZEST CLI는 프로젝트 관리, 서버 실행, 서비스 관리를 위한 명령줄 도구입니다.

## 기본 사용법

```bash
dizest <command> [options]
```

버전 확인:
```bash
dizest --version
```

---

## 프로젝트 관리 명령어

### install

새로운 DIZEST 프로젝트를 생성합니다.

#### 사용법

```bash
dizest install [PROJECT_NAME] [OPTIONS]
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `PROJECT_NAME` | string | ✓ | - | 생성할 프로젝트 디렉토리 이름 (최소 3자) |

#### 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|-----|------|--------|------|
| `--password` | string | 자동생성 | root 계정 비밀번호 |

#### 예제

```bash
# 기본 설치 (비밀번호 자동생성)
dizest install myproject

# 커스텀 비밀번호 지정
dizest install myproject --password mysecret123

# 출력 예시:
# dizest installed at `myproject`
# password: aB3dE5fG7hI9jK1l
```

#### 생성되는 구조

```
myproject/
├── config.py           # 프로젝트 설정
├── password            # bcrypt로 암호화된 비밀번호
├── project/            # 프로젝트 소스
│   └── main/
├── plugin/             # 플러그인 디렉토리
└── public/             # 공개 디렉토리
    └── app.py
```

---

### upgrade

기존 DIZEST 프로젝트를 최신 버전으로 업그레이드합니다.

#### 사용법

```bash
dizest upgrade
```

#### 실행 조건

- 현재 디렉토리에 `project/` 폴더가 존재해야 함
- 사용자 데이터는 보존되고 시스템 파일만 업데이트됨

#### 예제

```bash
cd myproject
dizest upgrade
```

#### 주의사항

- 업그레이드 전 프로젝트 백업 권장
- `project/` 디렉토리가 완전히 교체됨
- 커스텀 수정사항은 `plugin/` 디렉토리에 저장 권장

---

### password

Single 모드에서 root 사용자의 비밀번호를 변경합니다.

#### 사용법

```bash
dizest password <NEW_PASSWORD>
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `NEW_PASSWORD` | string | ✓ | 새로운 비밀번호 |

#### 예제

```bash
dizest password mynewpassword123
```

#### 보안 고려사항

- 비밀번호는 bcrypt로 암호화되어 저장됨
- 명령 히스토리에 비밀번호가 남을 수 있으므로 주의

---

## 서버 실행 명령어

### run

DIZEST 서버를 포그라운드로 실행합니다.

#### 사용법

```bash
dizest run [OPTIONS]
```

#### 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|-----|------|--------|------|
| `--host` | string | `0.0.0.0` | 웹 서버 호스트 주소 |
| `--port` | integer | `3000` | 웹 서버 포트 번호 |
| `--log` | string | `None` | 로그 파일 경로 (지정하지 않으면 stdout) |

#### 예제

```bash
# 기본 실행
dizest run

# 포트 지정
dizest run --port=4000

# 호스트와 포트 지정
dizest run --host=127.0.0.1 --port=8080

# 로그 파일 지정
dizest run --port=4000 --log=/var/log/dizest.log

# 외부 접속 허용
dizest run --host=0.0.0.0 --port=80
```

#### 접속

브라우저에서 `http://localhost:PORT` 접속

#### 중지

`Ctrl+C` 키를 눌러 서버 중지

---

### server

DIZEST 서버를 데몬으로 실행/중지합니다.

#### 사용법

```bash
dizest server <ACTION> [OPTIONS]
```

#### Actions

| Action | 설명 |
|--------|------|
| `start` | 서버를 백그라운드로 시작 |
| `stop` | 실행 중인 서버 중지 |

#### 옵션 (start 전용)

| 옵션 | 타입 | 기본값 | 설명 |
|-----|------|--------|------|
| `--host` | string | `0.0.0.0` | 웹 서버 호스트 |
| `--port` | integer | `3000` | 웹 서버 포트 |
| `--log` | string | `None` | 로그 파일 경로 |

#### 예제

```bash
# 데몬 시작
dizest server start

# 포트 지정하여 시작
dizest server start --port=4000

# 데몬 중지
dizest server stop
```

#### 프로세스 확인

```bash
# 실행 중인 dizest 프로세스 확인
ps aux | grep dizest
```

---

### kill

실행 중인 모든 DIZEST 서버 프로세스를 강제 종료합니다.

#### 사용법

```bash
dizest kill
```

#### 예제

```bash
dizest kill
```

#### 주의사항

- 모든 dizest 프로세스가 종료됨
- 진행 중인 워크플로우 실행도 중단됨
- 데이터 손실 가능성이 있으므로 주의

---

## 서비스 관리 명령어

### service

시스템 서비스로 DIZEST를 관리합니다 (Linux systemd).

#### 사용법

```bash
dizest service <ACTION>
```

#### Actions

| Action | 설명 |
|--------|------|
| `install` | systemd 서비스로 등록 |
| `uninstall` | systemd 서비스 등록 해제 |
| `start` | 서비스 시작 |
| `stop` | 서비스 중지 |
| `restart` | 서비스 재시작 |
| `status` | 서비스 상태 확인 |

#### 예제

```bash
# 서비스 등록
sudo dizest service install

# 서비스 시작
sudo dizest service start

# 서비스 상태 확인
sudo dizest service status

# 서비스 재시작
sudo dizest service restart

# 서비스 중지
sudo dizest service stop

# 서비스 등록 해제
sudo dizest service uninstall
```

#### 자동 시작 설정

```bash
# 서비스 등록 후
sudo systemctl enable dizest

# 부팅 시 자동 시작 비활성화
sudo systemctl disable dizest
```

#### 로그 확인

```bash
# systemd 로그 확인
sudo journalctl -u dizest -f
```

---

## 환경 변수

DIZEST는 다음 환경 변수를 지원합니다:

| 환경 변수 | 설명 | 기본값 |
|----------|------|--------|
| `DIZEST_HOST` | 기본 서버 호스트 | `0.0.0.0` |
| `DIZEST_PORT` | 기본 서버 포트 | `3000` |
| `DIZEST_LOG` | 기본 로그 파일 경로 | `None` |

#### 사용 예제

```bash
# 환경 변수로 서버 실행
export DIZEST_PORT=4000
dizest run

# 일회성 설정
DIZEST_PORT=5000 dizest run
```

---

## 전체 워크플로우 예제

### 1. 새 프로젝트 시작

```bash
# 프로젝트 생성
dizest install myai

# 프로젝트로 이동
cd myai

# 서버 실행
dizest run --port=4000
```

### 2. 운영 환경 배포

```bash
# 프로젝트 생성 (서버에서)
dizest install production --password securepassword123

cd production

# systemd 서비스 등록
sudo dizest service install

# 서비스 시작
sudo dizest service start

# 자동 시작 활성화
sudo systemctl enable dizest

# 상태 확인
sudo dizest service status
```

### 3. 업그레이드

```bash
# DIZEST 패키지 업그레이드
pip install dizest --upgrade

# 프로젝트 업그레이드
cd myproject
dizest upgrade

# 서버 재시작 (데몬 모드인 경우)
dizest server stop
dizest server start
```

---

## 문제 해결

### 포트가 이미 사용 중

```bash
# 포트를 사용 중인 프로세스 확인
lsof -i :3000

# 프로세스 종료
kill <PID>

# 또는 다른 포트 사용
dizest run --port=4000
```

### 권한 오류

```bash
# 1024 이하의 포트는 root 권한 필요
sudo dizest run --port=80

# 또는 1024 이상의 포트 사용
dizest run --port=8080
```

### 서버가 시작되지 않음

```bash
# 로그 확인
dizest run --log=debug.log

# 또는
cat debug.log
```

### 비밀번호 분실

```bash
# 비밀번호 재설정
dizest password newpassword123
```

---

## 관련 문서

- [사용 가이드](../usage-guide.md)
- [Workflow API](workflow.md)
- [Serve API](serve.md)
