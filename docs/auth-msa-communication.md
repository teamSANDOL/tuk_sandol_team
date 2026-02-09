# MSA 서비스간 통신 인증 절차

## 목적

기존 Gateway 서명 검증 중심 구조를 폐기하고, 각 MSA가 Keycloak Access Token을 직접 검증하는 구조로 전환한다.

관련 용어: [Access Token](./glossary.md#access-token), [JWKS](./glossary.md#jwks-json-web-key-set), [X-User-ID](./glossary.md#x-user-id)

## 이 문서를 읽는 방법 (인증 초심자용)

- 이 문서는 "MSA API를 호출할 때 어떤 헤더를 붙이고, 서버가 무엇을 검증해야 하는가"를 설명한다.
- 인증은 "누구인지 확인(401)"과 "권한 있는지 확인(403)"로 나뉜다.
- 서비스는 헤더 문자열 자체를 신뢰하지 않고, JWT 검증 결과를 기준으로 최종 판단해야 한다.

## 표준 계약

### 필수 헤더

- `Authorization: Bearer <access_token>`
- `X-User-ID: <keycloak_sub>`

요약:

- `Authorization`은 "이 요청이 어떤 사용자 토큰으로 왔는지" 증명하는 값이다.
- `X-User-ID`는 "비즈니스 로직에서 쉽게 쓰는 사용자 식별자"다.
- 산돌이 표준에서는 `X-User-ID` 값이 토큰의 `sub`와 정확히 같아야 한다.

### 금지/폐기

- `X-Signature` 기반 Gateway 사용자 HMAC 인증
- 사용자 인증 근거로 `X-User-ID` 헤더만 단독 신뢰

## 검증 책임 분리

### Gateway

- 라우팅/관측/기본 차단(헤더 누락)까지만 담당
- 사용자 인증의 최종 판정자는 아님

### 각 MSA

- [JWT](./glossary.md#jwt) 서명 검증 (JWKS)
- `iss`/`aud`/`exp`/`nbf`/`iat` 검증
- 토큰의 사용자 식별자와 `X-User-ID` 정합성 검증
- 권한 클레임(`realm_access.roles`, `resource_access`) 검증

## API 요청/응답 규약 (MSA 공통)

### 요청 헤더 규약

| 헤더 | 예시 | 필수 | 설명 |
|---|---|---|---|
| `Authorization` | `Bearer eyJ...` | O | Keycloak Access Token |
| `X-User-ID` | `2f1a0d...` | O | Keycloak `sub` 그대로 전달 |
| `Content-Type` | `application/json` | O(Body 있을 때) | JSON 요청 본문 타입 |

### 보호 API 호출 예시

```http
POST /meal/api/v1/bookmark HTTP/1.1
Host: sandol.example.com
Authorization: Bearer <access_token>
X-User-ID: 2f1a0d54-93e2-4ad8-b7da-6cfd0d0a1234
Content-Type: application/json

{
  "restaurant_id": 12
}
```

### 성공 응답 예시

```json
{
  "status": "ok",
  "data": {
    "restaurant_id": 12,
    "bookmarked": true
  }
}
```

### 실패 응답 예시 (권장 포맷)

401 (인증 실패):

```json
{
  "error": "TOKEN_SIGNATURE_INVALID",
  "message": "Access token signature verification failed"
}
```

403 (인가 실패):

```json
{
  "error": "FORBIDDEN",
  "message": "Required role is missing"
}
```

## 요청 처리 순서 (MSA 공통)

1. `Authorization`/`X-User-ID` 헤더 존재 확인
2. Bearer 토큰 파싱 실패 시 401
3. OIDC discovery에서 `issuer`, `jwks_uri` 확보(캐시)
4. `kid`로 JWKS 키 선택 후 서명 검증
5. `iss`/`aud`/시간 클레임 검증
6. 토큰 `sub`와 `X-User-ID` 값이 정확히 같은지 비교
7. 권한 부족 시 403, 성공 시 핸들러 진입

## 검증 포인트 상세

### 1) 헤더 존재/형식 검증

- `Authorization` 누락/포맷 불일치 -> 401
- `X-User-ID` 누락 -> 401

### 2) 서명 검증

- 토큰 header의 `kid`로 JWKS 공개키 선택
- 허용된 `alg`만 수용 (`none` 금지)

### 3) 클레임 검증

- `iss`: 사전 설정값과 정확 일치
- `aud`: 현재 서비스 audience 포함
- `exp`/`nbf`/`iat`: 시간 유효성

### 4) 사용자 정합성 검증

- 토큰 `sub` == `X-User-ID`인지 검사
- 불일치 시 401 (토큰 위임/변조 가능성)

### 5) 권한 검증

- 전역 권한: `realm_access.roles`
- 서비스 권한: `resource_access[service_client_id].roles`
- 권한 부족 시 403

## 에러 코드 정책

- 401: 토큰 없음/무효/만료/검증 실패/식별자 불일치
- 403: 인증은 성공했으나 권한 부족

## 코드베이스 정합성 메모 (현재)

- `sandol-gateway/gateway/lua/signature_verify.lua`는 `X-User-ID` + `X-Signature` 기반 검증을 수행하고 있어 폐기 대상.
- 일부 gateway route는 `X-User-Sub`를 전달하고 있어 `X-User-ID` 표준으로 정리 필요.
- 일부 서비스는 이미 `X-User-ID` 기반 로직을 사용 중.

## 전환 체크포인트

1. Gateway 라우트에서 `X-User-ID` 전달 표준화
2. Gateway HMAC 인증 Lua 우회/제거
3. 각 MSA에 공통 JWKS 검증 모듈 적용
4. 통합 테스트에서 "유효 토큰 + 잘못된 X-User-ID" 케이스 필수 검증

## 참고 문헌

- Keycloak OIDC: https://www.keycloak.org/securing-apps/oidc-layers
- OIDC Discovery 1.0: https://openid.net/specs/openid-connect-discovery-1_0.html
- RFC 8725 (JWT BCP): https://www.rfc-editor.org/rfc/rfc8725.html
- RFC 9068 (JWT Access Token Profile): https://www.rfc-editor.org/rfc/rfc9068.html
