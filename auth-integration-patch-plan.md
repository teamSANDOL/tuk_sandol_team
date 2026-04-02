# Kakao-Bot ↔ Auth-Relay ↔ Keycloak 연동 패치 플랜

## 문서 목적

- 이 문서는 `sandol_kakao_bot_service` / `sandol-auth-relay` / Gateway / Keycloak 설정 연동을 단계별로 보강하기 위한 실행 계획이다.
- 목표는 **보안 경계 강화**, **콜백 신뢰성 확보**, **운영 안전성 향상**이다.
- 범위에서 **Auth-Relay webhook WIP**(`webhooks/kakao/unlink`)는 제외한다.

## 적용 범위

- 포함
  - 로그인 링크 발급 (`POST /relay/issue_login_link`)
  - 로그인 리다이렉트 (`GET /relay/login/{lit}`)
  - OIDC 콜백 (`GET /relay/oidc/callback`)
  - 챗봇 콜백 (`POST /kakao-bot/users/callback`)
  - 토큰 저장/갱신 및 MSA 호출 헤더 전달
- 제외
  - `sandol-auth-relay` webhook 관련 코드/설정

## 사전 조건

- 배포 전 운영 시크릿 교체 계획이 준비되어 있어야 한다.
- Keycloak 클라이언트(`sandol-kakao-bot`) 설정 변경 권한이 있어야 한다.
- 스테이징 환경에서 E2E 인증 리허설이 가능해야 한다.

## 우선순위 요약

1. High: callback URL 신뢰 경계 고정
2. High: bot 콜백의 `issuer/aud/client_key` + JWT 검증 강화
3. High: 시크릿 하드코딩 제거/회전
4. Medium: allowlist 정책 키/형식 정합성 수정
5. Medium: gateway `X-User-ID` 신뢰 모델 보강
6. Medium: 테스트/관측/롤백 체계 보강

---

## Phase 0 - 긴급 안전조치 (배포 전)

### 목표

- 이미 노출되었을 가능성이 있는 시크릿 위험을 먼저 줄인다.

### 작업 항목

- [x] Keycloak `sandol-kakao-bot` client secret 재발급
- [x] Relay HMAC 시크릿(`RELAY_TO_CHATBOT_HMAC_SECRET`) 교체
- [x] Bot HMAC 시크릿(`RELAY_CLIENT_SECRETS`) 동기화 교체
- [ ] `clients.json`의 평문 시크릿 제거 계획 확정

### 관련 위치

- `sandol-auth-relay/app/config/clients.json`
- `sandol-auth-relay/app/config/config.py`
- `sandol_kakao_bot_service/app/config/config.py`
- `sandol_user_service/base_data/Sandori-realm.noauthz.json` (운영 반영 시점과 별개로 참조)

### 완료 기준

- 운영/스테이징에서 더 이상 기본/노출 시크릿이 사용되지 않는다.
- 시크릿 교체 이후 로그인 플로우가 정상 동작한다.

---

## Phase 1 - Auth-Relay 발급 경계 고정

### 목표

- `issue_login_link` 요청자가 임의 `callback_url`을 주입해 토큰을 외부로 유출할 수 없게 한다.

### 변경 파일

- `sandol-auth-relay/app/routers/auth.py`
- `sandol-auth-relay/app/schemas/auth.py`
- `sandol-auth-relay/app/utils/clients.py`
- `sandol-auth-relay/app/config/clients.json`
- (선택) `docs/auth-chatbot-auth-relay.md`

### 작업 항목 (구현 순서)

1. [x] `client_key`별 고정 callback URL 필드 추가
   - `clients.json`에 `callback_url`(정확한 절대 URL) 명시
   - `ClientConfig`가 이 필드를 필수 검증하도록 추가
2. [x] `IssueLinkReq.callback_url` 신뢰모델 변경
   - 권장안: 요청 바디의 `callback_url` 제거
   - 대안안: 입력은 받되 반드시 `client_key` 고정값과 exact match 검증
3. [x] `issue_login_link`에서 callback URL을 서버측 값으로 강제
   - 세션 저장(`sess_set`) 시 검증된 값만 보관
4. [ ] `POST /issue_login_link` 호출 인증 추가
   - 최소 공유시크릿 HMAC 헤더 검증(서비스 간 호출 전용)
   - 실패 시 `401` 즉시 반환

### 완료 기준

- 임의 callback URL로 로그인 링크 발급이 불가능하다.
- 인증되지 않은 발급 요청은 거부된다.

### 검증 시나리오

- 정상 `client_key` + 정상 호출 인증 → `200`
- callback URL 변조 시도 → `400/401`
- 인증 헤더 누락 → `401`

---

## Phase 2 - Bot 콜백 토큰/클레임 검증 강화

### 목표

- 서명된 Relay 콜백이라도 토큰/메타데이터 위변조나 설정 불일치를 확실히 차단한다.

### 변경 파일

- `sandol_kakao_bot_service/app/routers/user.py`
- `sandol_kakao_bot_service/app/services/auth_service.py`
- `sandol_kakao_bot_service/app/schemas/auth.py`
- (필요시) `sandol_kakao_bot_service/app/config/config.py`

### 작업 항목 (구현 순서)

1. [x] `issuer/aud/client_key` 정합성 검증 추가
   - `issuer == Config.KC_SERVER_URL + realms/...` 또는 명시 issuer 값 비교
   - `aud == Config.KC_CLIENT_ID`
   - `client_key == Config.KC_CLIENT_ID`
2. [~] access token 검증 방식 교체
    - 금지: `jwt.decode(..., verify_signature=False)`
    - 현재: `exp/iss/sub` + `azp` 우선, `aud` fallback 검증
    - 적용 예정: Keycloak JWKS 기반 서명 검증
3. [x] 실패 코드 정리
   - 검증 실패는 `401` 중심으로 표준화
   - 내부 오류만 `500`
4. [ ] 로그 민감정보 점검
   - 토큰 본문/시크릿 직접 로그 금지

### 완료 기준

- 서명/nonce/timestamp 통과 후에도 `issuer/aud/client_key` 불일치면 차단된다.
- access token은 현재 `exp/iss/sub`와 `azp` 우선, `aud` fallback 검증을 거친다.
- JWKS 서명 검증은 별도 후속 단계로 남아 있다.

### 검증 시나리오

- 정상 토큰/클레임 → `200`
- `aud` 불일치 토큰 → `401`
- 만료 토큰 → `401`
- 잘못된 `client_key` payload → `401`

---

## Phase 3 - Secret Hygiene 정비

### 목표

- 시크릿이 코드/파일에 평문 저장되지 않도록 하고, 운영 시 fail-fast를 보장한다.

### 변경 파일

- `sandol-auth-relay/app/config/clients.json`
- `sandol-auth-relay/app/config/config.py`
- `sandol-auth-relay/app/utils/clients.py`
- `.env.example` (relay/bot)
- 배포 문서

### 작업 항목

1. [ ] `clients.json`에서 `client_secret` 제거
2. [ ] env 주입만 허용하도록 검증 강화
3. [ ] Relay도 non-debug에서 기본/빈 시크릿 사용 시 부팅 실패 처리
4. [ ] 시크릿 네이밍 규약 문서화 (`<CLIENT_KEY>__SECRETS`)

### 완료 기준

- 저장소 평문 시크릿이 제거된다.
- 잘못된 시크릿 구성은 애플리케이션 시작 단계에서 차단된다.

---

## Phase 4 - Redirect/Allowlist 정책 정합성 수정

### 목표

- `redirect_after_allowlist`와 `callback_allowlist` 의미를 명확히 분리하고 코드와 설정을 일치시킨다.

### 변경 파일

- `sandol-auth-relay/app/routers/auth.py`
- `sandol-auth-relay/app/utils/redirects.py`
- `sandol-auth-relay/app/config/clients.json`

### 작업 항목

1. [x] 최종 사용자 리다이렉트 검증에는 `redirect_after_allowlist`만 사용
2. [x] callback URL 검증은 별도 함수로 분리 (절대 URL exact match)
3. [x] 상대경로 정책과 절대 URL 정책을 혼합하지 않도록 스키마 정리
4. [ ] dead config(사용 안되는 allowlist 항목) 제거

### 완료 기준

- 정책 키가 목적별로 1:1 매핑된다.
- 의도하지 않은 우회 경로가 제거된다.

---

## Phase 5 - Gateway 경계 강화

### 목표

- 외부에서 주입된 `X-User-ID`를 그대로 신뢰하는 위험을 낮춘다.

### 변경 파일

- `sandol-gateway/gateway/routes/kakao-bot.conf`
- `sandol-gateway/gateway/routes/auth-relay.conf`
- (필요시) gateway 공통 설정

### 작업 항목

1. [ ] 외부 입력 `X-User-ID` 전달 차단(삭제 또는 재정의)
2. [ ] 내부 trusted hop에서만 `X-User-ID` 주입하는 규칙 수립
3. [ ] 민감 API는 내부 네트워크에서만 접근 가능하도록 정책 보강

### 완료 기준

- 클라이언트가 임의 `X-User-ID`로 권한 상승 시도 불가.

---

## Phase 6 - 테스트/검증/배포

### 테스트 범위

- 단위 테스트
  - [ ] relay: callback URL 검증기
  - [ ] relay: issue_login_link 인증 헤더 검증
  - [ ] bot: issuer/aud/client_key 검증기
  - [ ] bot: JWT 검증 성공/실패 케이스
- 통합 테스트
  - [ ] 로그인 링크 발급 → callback 저장까지 정상 흐름
  - [ ] 변조 payload/만료 토큰/reused nonce 차단
  - [ ] relay `/oidc/callback`의 callback timeout/invalid status 경로 확인
  - [ ] refresh token 갱신 및 교체 저장 확인

### 실행 커맨드 (각 서비스 루트에서)

- relay
  - `uv run ruff check .`
  - `uv run mypy .`
  - `uv run pytest`
- kakao-bot
  - `uv run ruff check .`
  - `uv run mypy .`
  - `uv run pytest`

### 배포 순서 (권장)

1. [ ] 시크릿 선교체 (staging)
2. [ ] relay 배포
3. [ ] kakao-bot 배포
4. [ ] gateway 배포
5. [ ] E2E 로그인 점검
6. [ ] 운영 반영

### 롤백 기준

- 로그인 링크 발급 실패율 급증
- `/users/callback` 401 비율 비정상 급증
- 토큰 refresh 실패(`invalid_grant`) 급증

롤백 시에는 코드와 시크릿 버전을 함께 맞춰야 한다.

---

## 체크리스트 (릴리즈 게이트)

- [ ] callback URL이 요청자 입력값에 의해 결정되지 않는다.
- [x] bot 콜백에서 `issuer/aud/client_key`를 모두 검증한다.
- [ ] bot이 access token 서명/클레임 검증 후에만 `sub`를 사용한다.
- [ ] 저장소 평문 시크릿이 제거되었다.
- [ ] relay/bot 모두 non-debug에서 시크릿 fail-fast가 동작한다.
- [x] allowlist 정책 키가 코드/설정에서 일관된다.
- [ ] gateway가 외부 주입 `X-User-ID`를 신뢰하지 않는다.
- [ ] webhook WIP는 본 변경에서 제외되었다.

## 예상 일정

- Phase 0: 0.5일
- Phase 1~2: 1.0~1.5일
- Phase 3~4: 0.5~1.0일
- Phase 5~6: 0.5~1.0일
- 총 2.5~4.0일 (스테이징 리허설 포함)
