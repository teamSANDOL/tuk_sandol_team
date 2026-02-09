# AGENTS.md - 산돌이 프로젝트 (tuk_sandol_team)

## 프로젝트 개요

**산돌이**는 한국공학대학교 학생 및 관계자 6,200+ 명이 사용하는 **카카오톡 챗봇 서비스**입니다.
MSA(Microservice Architecture) 기반으로 구성되어 Docker Compose로 통합 운영됩니다.

### 서비스 구성 (서브모듈)

| 서비스 | 기술 스택 | 역할 |
|--------|-----------|------|
| `sandol_kakao_bot_service` | FastAPI + SQLite | 카카오톡 챗봇 메인 서버 |
| `sandol_meal_service` | FastAPI + PostgreSQL | 학식 메뉴 API |
| `sandol-auth-relay` | FastAPI | Keycloak 인증 중계 서버 |
| `sandol-gateway` | OpenResty (Nginx + Lua) | API Gateway, 서명 인증 |
| `sandol_notice_notification` | NestJS + PostgreSQL + RabbitMQ | 공지사항 알림 서버 |
| `sandol_classroom_timetable_service` | Express.js | 강의실 시간표 API |
| `sandol_user_service` | Keycloak | 사용자 인증/권한 중앙 관리 |
| `sandol-static-info-service` | FastAPI | 정적 정보 API |

---

## Build / Lint / Test Commands

### 전체 서비스 실행

```bash
# 서브모듈 초기화 및 업데이트
git submodule update --init --recursive
git submodule foreach 'git checkout main && git pull origin main'

# 환경 변수 설정 (.env.example → .env 복사)
cp ./<submodule>/.env.example ./<submodule>/.env

# 전체 서비스 실행
docker compose up --build -d              # 프로덕션
docker compose -f docker-compose.dev.yml up -d  # 개발

# 서비스 중지
docker compose down
```

### Python 서비스 (kakao-bot, meal, auth-relay, static-info)

```bash
# 의존성 설치 (uv 사용)
uv sync

# 린트 및 포맷팅
uv run ruff check .                    # 린트 검사
uv run ruff check . --fix              # 린트 자동 수정
uv run ruff format .                   # 코드 포맷팅

# 타입 체크
uv run mypy .

# 로컬 서버 실행 (예: kakao-bot)
uv run uvicorn main:app --host 0.0.0.0 --port 5600 --reload

# DB 마이그레이션
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "migration message"
```

### Node.js 서비스 (notice-notification, classroom-timetable)

```bash
# notice-notification (NestJS)
npm install
npm run lint                           # ESLint + Prettier
npm run test                           # Jest 단위 테스트
npm run test:e2e                       # E2E 테스트
npm run start:dev                      # 개발 서버

# classroom-timetable (Express)
npm install
npm run start
```

---

## 코드 스타일 가이드라인

### Python (모든 Python 서비스 공통)

- **Python 버전**: 3.11 (>=3.11, <3.12) 권장, 최소 3.11
- **린터/포매터**: Ruff, Black
- **Line length**: 88자
- **Quote style**: Double quotes (`"`)
- **Docstring**: Google style
- **타입 힌팅**: 모든 함수에 필수

#### Import 순서 (Ruff/isort)
```python
# 1. 표준 라이브러리
import asyncio
from typing import Annotated

# 2. 서드파티
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

# 3. 로컬 모듈
from app.config import Config, logger
from app.services.auth_service import verify_relay_signature
```

#### 네이밍 컨벤션
- 함수/변수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- Router prefix: `/{feature}` (예: `/meal`, `/kakao-bot`)

### TypeScript/JavaScript (NestJS, Express)

- **린터**: ESLint + Prettier
- **Quote style**: Single quotes (`'`)
- **Semicolons**: Required

---

## 인증 아키텍처 (Auth-Relay + Keycloak)

### 전체 인증 흐름

```
사용자(챗봇) → Kakao Bot Service → Auth Relay → Keycloak
                    ↓                    ↓
              토큰 저장 (암호화)    Access/Refresh Token 발급
                    ↓
              MSA 호출 시 Authorization + X-User-ID 헤더 전달
                    ↓
              Gateway → 각 도메인 MSA
```

### 1. 로그인 링크 발급 (`POST /issue_login_link`)

Kakao Bot Service가 Auth Relay에 요청:
```json
{
  "chatbot_user_id": "kakao_user_id",
  "callback_url": "http://kakao-bot-service/callback",
  "client_key": "kakao-bot",
  "redirect_after": "https://example.com/success"
}
```

### 2. 사용자 로그인 (`GET /login/{lit}`)

- LIT(Login Initiation Token) 검증
- PKCE 파라미터 생성 (state, nonce, code_verifier)
- Keycloak 인가 URL로 리다이렉트

### 3. OIDC 콜백 (`GET /oidc/callback`)

- Authorization Code → Token 교환 (scope: `openid offline_access`)
- 챗봇 서버에 토큰 전달 (X-Relay-Signature HMAC 서명 포함)
- 페이로드 구조:
```json
{
  "relay_access_token": "<access_token>",
  "offline_refresh_token": "<refresh_token>",
  "issuer": "https://auth.example.com/realms/Sandori",
  "chatbot_user_id": "user-123",
  "expires_in": 300,
  "refresh_expires_in": 0,
  "ts": 1700000000,
  "nonce": "<random>"
}
```

### 4. 챗봇 서버 토큰 관리

- **서명 검증**: HMAC-SHA256 (canonical JSON + base64url)
- **토큰 저장**: Fernet 암호화 후 DB 저장
- **사용자 매핑**: `keycloak_sub` ↔ `kakao_id` 연결
- **토큰 갱신**: Refresh Token으로 Access Token 자동 갱신

### HTTP 헤더 규약 (MSA 간 통신)

| 헤더 | 필수 | 설명 |
|------|------|------|
| `Authorization: Bearer <token>` | O | Keycloak Access Token |
| `X-User-ID` | O | 사용자 식별자 (MSA 간 통신용) |
| `X-Relay-Signature` | Relay→Bot만 | HMAC 서명 |

> **참고**: Auth-Relay 등 인증 절차 내부에서는 Keycloak `sub` 클레임을 사용할 수 있으나, 일반 MSA 간 통신에서는 `X-User-ID`를 사용합니다.

---

## 에러 처리 패턴

### 카카오톡 챗봇 (핵심!)

**카카오톡은 200 외의 응답을 무시**하므로 모든 에러도 200으로 반환:

```python
from app.utils.kakao import KakaoError, NotAuthorizedError

# 일반 에러
raise KakaoError("등록된 식당이 없습니다.")

# 인증 에러
raise NotAuthorizedError()
raise LoginRequiredError(message="다시 로그인해주세요.")
```

### 인증 관련 HTTP 코드

| 상황 | 코드 | 처리 |
|------|------|------|
| 토큰/X-User-ID 누락 | 401 | Unauthorized |
| 서명 검증 실패 | 401 | Invalid signature |
| 권한 부족 | 403 | Forbidden |
| 계정 충돌 | 409 | 이미 다른 계정과 연결됨 |

---

## 프로젝트 구조 (Python 서비스 공통)

```
app/
├── config/         # 설정, 상수, 로거
├── models/         # SQLAlchemy ORM 모델
├── routers/        # FastAPI 라우터
├── schemas/        # Pydantic 요청/응답 스키마
├── services/       # 비즈니스 로직
├── utils/          # 유틸리티 함수
└── middleware/     # 미들웨어 (선택)
main.py             # FastAPI 엔트리포인트
pyproject.toml      # uv/PEP 621 의존성
alembic/            # DB 마이그레이션
```

---

## 환경 변수 (주요)

### 공통
```env
SECRET_KEY=***                          # Gateway 서명용
```

### kakao-bot-service
```env
DEBUG=False
KC_SERVER_URL=https://sandol.sio2.kr/auth/
KC_CLIENT_ID=kakao-bot
KC_CLIENT_SECRET=***
TOKEN_ENCRYPTION_KEY=***                # Fernet 암호화 키
AUTH_RELAY_URL=http://auth-relay:8000/relay
MEAL_SERVICE_URL=http://meal-service:80/meal
```

### auth-relay
```env
BASE_URL=https://relay.example.com
JWT_SECRET=***                          # LIT 서명용
RELAY_TO_CHATBOT_HMAC_SECRET=***        # 콜백 HMAC 서명용
STATE_TTL_SECONDS=600
```

---

## 새 서비스 통합 절차

1. **docker-compose.yml에 서비스 추가**
2. **Git Submodule 등록**: `git submodule add <url> ./<folder>`
3. **Gateway Route 설정**: `sandol-gateway/gateway/routes/`에 conf 추가
4. **PR 생성** (Gateway 설정 PR이 먼저 머지되어야 함)

---

## 주의사항

1. **카카오톡 응답은 반드시 200**: 에러도 `KakaoError`로 200 반환
2. **토큰 평문 로깅 금지**: 암호화 후 저장, 로그에 노출 금지
3. **타입 안전성**: `type: ignore`, `as any` 등 타입 무시 금지
4. **서명 검증 필수**: Relay 콜백은 HMAC + timestamp + nonce 검증
5. **Offline Token 관리**: 20~25일 내 최소 1회 refresh 필요 (Idle Timeout)

---

## 문의

- [산돌이 디스코드](https://discord.com/channels/1339452791071969331)
- [GitHub Issues](https://github.com/teamSANDOL/tuk_sandol_team/issues)
