# Temporary Web Service for SSO Testing

Keycloak SSO 기능을 테스트하기 위한 간단한 FastAPI 웹서버입니다.

## 기능

- **홈페이지 (`/`)**: 로그인 상태에 따라 다른 화면 표시
- **로그인 (`/login`)**: Keycloak 인증 페이지로 리다이렉트
- **콜백 (`/callback`)**: OAuth2 인증 코드를 토큰으로 교환
- **로그아웃 (`/logout`)**: Keycloak 로그아웃
- **보호된 페이지 (`/protected`)**: 인증이 필요한 API 엔드포인트
- **헬스체크 (`/health`)**: 서비스 상태 확인

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

서버는 http://localhost:8011 에서 실행됩니다.

## Docker 실행

```bash
# 이미지 빌드
docker build -t temp-web-service .

# 컨테이너 실행
docker run -p 8011:8011 --env-file .env temp-web-service
```

## Keycloak 클라이언트 설정

Keycloak에서 다음과 같이 클라이언트를 설정해야 합니다:

- **Client ID**: `temp-web-service`
- **Client Type**: `OpenID Connect`
- **Client authentication**: `On` (Confidential)
- **Valid redirect URIs**: `http://localhost:8011/callback`
- **Valid post logout redirect URIs**: `http://localhost:8011/`
- **Web origins**: `http://localhost:8011`

## 환경 변수

`.env` 파일에서 다음 변수들을 설정할 수 있습니다:

- `KEYCLOAK_BASE_URL`: Keycloak 서버 URL (기본값: http://localhost:8010/auth)
- `KEYCLOAK_REALM`: Keycloak 렐름 이름 (기본값: sandol)
- `KEYCLOAK_CLIENT_ID`: 클라이언트 ID (기본값: temp-web-service)
- `KEYCLOAK_CLIENT_SECRET`: 클라이언트 시크릿
