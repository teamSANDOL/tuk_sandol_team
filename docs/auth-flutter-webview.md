# Flutter WebView 인증 가이드 (Auth-Relay 미사용)

## 목적

Flutter 앱이 Auth-Relay 없이 앱 내부 WebView로 직접 OIDC 인증을 수행할 때의 표준 절차와 보안 요구사항을 정의한다.

관련 용어: [OIDC](./glossary.md#oidc-openid-connect), [PKCE](./glossary.md#pkce), [offline_access](./glossary.md#offline_access)

## 권장 전제

- 보안 우선순위는 "외부 브라우저(AppAuth) > 인앱 WebView"다.
- 제품 요구로 WebView를 사용해야 할 때만 이 문서를 따른다.

## 표준 인증 절차

1. 앱에서 PKCE(`code_verifier`, `code_challenge`) 생성
2. `state`, `nonce` 생성 후 인증 URL 오픈
3. WebView에서 Keycloak 로그인
4. 등록된 redirect URI로 code 수신
5. 앱 백엔드 또는 앱 안전 구역에서 code -> token 교환
6. Access/Refresh Token 저장(플랫폼 secure storage)
7. API 호출 시 `Authorization` 헤더 부착

## API 요청/응답 상세 (Flutter 직접 처리 시)

### 1) Authorization 요청

앱이 WebView로 여는 URL 예시:

```text
GET https://<kc-host>/realms/<realm>/protocol/openid-connect/auth
  ?client_id=<client_id>
  &redirect_uri=<url-encoded-redirect-uri>
  &response_type=code
  &scope=openid%20profile%20email%20offline_access
  &state=<random_state>
  &nonce=<random_nonce>
  &code_challenge=<pkce_challenge>
  &code_challenge_method=S256
```

필드 설명:

| 파라미터 | 필수 | 설명 |
|---|---|---|
| `client_id` | O | Keycloak 클라이언트 ID |
| `redirect_uri` | O | 앱에 등록된 콜백 URI |
| `response_type` | O | `code` 고정 |
| `scope` | O | 최소 `openid`; 장기 갱신 필요 시 `offline_access` 포함 |
| `state` | O | CSRF 방지 값 |
| `nonce` | O | 토큰 재사용 방지 보조 값 |
| `code_challenge` | O | PKCE challenge |
| `code_challenge_method` | O | `S256` 고정 |

### 2) Redirect 수신

성공 시 리다이렉트 URI 예시:

```text
myapp://oauth/callback?code=<authorization_code>&state=<state>
```

검증 규칙:

- 쿼리 `state`가 요청 시 저장한 값과 같아야 함
- URI 스킴/호스트/경로가 등록한 redirect URI와 정확히 일치해야 함

### 3) Token 교환 요청

```http
POST https://<kc-host>/realms/<realm>/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=<client_id>
&code=<authorization_code>
&redirect_uri=<redirect_uri>
&code_verifier=<pkce_verifier>
```

성공 응답 예시:

```json
{
  "access_token": "<jwt>",
  "expires_in": 300,
  "refresh_expires_in": 0,
  "refresh_token": "<refresh_token>",
  "token_type": "Bearer",
  "scope": "openid profile email offline_access"
}
```

대표 실패 예시:

```json
{
  "error": "invalid_grant",
  "error_description": "Code not valid"
}
```

### 4) Refresh 요청

```http
POST https://<kc-host>/realms/<realm>/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&client_id=<client_id>
&refresh_token=<refresh_token>
```

운영 규칙:

- 새 `refresh_token`이 응답에 오면 기존 값을 즉시 교체
- `invalid_grant` 발생 시 로컬 토큰 삭제 후 재로그인 시작

## 필수 보안 요구사항

- `state` 불일치 즉시 실패 처리
- `nonce` 불일치 즉시 실패 처리
- PKCE는 `S256`만 허용
- Redirect URI allowlist 강제
- WebView의 JS bridge 최소화(불필요한 인터페이스 제거)
- 토큰/인가코드 URL 로깅 금지
- 스크린샷/백업 경로 토큰 노출 차단

## 플랫폼 주의점

### Android

- Intent/deep link hijacking 방지 설정 필수
- 디버그 빌드에서 network security config 점검

### iOS

- Universal Link 우선, custom scheme는 충돌/가로채기 검토
- Keychain 접근 정책(백그라운드/복원) 명시

## offline_access 운용

- 모바일에서 장기 refresh token 보관 시 위험도가 높다.
- 가능한 경우 refresh는 서버 위임(BFF 패턴) 검토.
- 앱 저장 시에는 반드시 OS 보안 저장소 사용.

## 금지사항

- WebView 내부 JS 변수/LocalStorage에 refresh token 저장
- 토큰 검증 생략 후 클레임만 사용
- `state`/`nonce` 검증 생략

## 참고 문헌

- OAuth 2.0 for Native Apps (RFC 8252): https://datatracker.ietf.org/doc/html/rfc8252
- OAuth 2.0 Security Best Current Practice (draft): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- OpenID Connect Core 1.0: https://openid.net/specs/openid-connect-core-1_0.html
