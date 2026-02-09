# JWKS 검증 공통 모듈 제작 가이드라인

## 목적

언어/프레임워크 최초 사용 개발자도 동일한 보안 기준으로 Access Token을 검증할 수 있도록 공통 모듈 계약을 정의한다.

관련 용어: [JWKS](./glossary.md#jwks-json-web-key-set), [kid](./glossary.md#kid), [Fail Closed](./glossary.md#fail-closed)

## 설계 원칙

- 서비스 코드에서 JWT 라이브러리를 직접 난립 사용하지 않는다.
- 검증 로직은 공통 모듈 1곳으로 집중한다.
- 검증 실패는 항상 실패로 처리(Fail Closed).
- discovery/JWKS 조회는 캐시 + 강제 refresh 1회 재시도까지만 허용.

## 모듈 표준 인터페이스

```text
verifyAccessToken(token, options) -> VerifiedPrincipal | VerificationError
```

초심자 설명:

- `token`: 클라이언트가 보낸 Bearer 토큰 문자열
- `options`: 이 서비스가 허용하는 issuer/audience/alg 같은 정책
- 반환값이 `VerifiedPrincipal`이면 "검증 완료된 사용자 컨텍스트"로 간주
- 에러면 즉시 401/403으로 처리하고 비즈니스 로직에 진입하지 않음

예시(개념):

```text
input token: eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9...
input options:
  expectedIssuer=https://sandol.example.com/auth/realms/Sandori
  expectedAudience=meal-service
  allowedAlgorithms=[RS256]
  clockSkewSeconds=120

output VerifiedPrincipal:
  subject=2f1a0d54-...
  userId=2f1a0d54-...   # X-User-ID로 사용
  roles=[global_user, meal_admin]
```

`options` 최소 필드:

- expectedIssuer
- expectedAudience (service 단위)
- allowedAlgorithms (예: RS256)
- clockSkewSeconds

`VerifiedPrincipal` 최소 필드:

- subject
- userId (`X-User-ID` 값, 즉 Keycloak `sub`)
- roles (realm/client roles 통합 표현)
- rawClaims

## 필수 검증 항목

1. JWT 형식/서명
2. `alg` allowlist (`none` 금지)
3. `kid` 기반 JWKS 키 선택
4. `iss` 정확 일치
5. `aud` 포함 여부
6. `exp`/`nbf`/`iat` 시간 검증
7. 필요 시 `typ`, `azp` 정책 검증

검증 순서 권장:

1. 토큰 파싱 실패 여부 확인
2. `alg` 허용 목록 검증
3. `kid`로 JWKS 키 조회
4. 서명 검증
5. 클레임(`iss`, `aud`, `exp`, `nbf`, `iat`) 검증
6. 프로젝트 정합성(`sub == X-User-ID`) 검증

## 캐시/키 로테이션 정책

- OIDC discovery 및 JWKS 응답 TTL 캐시
- 검증 중 `kid` 미일치 시 JWKS 강제 갱신 후 1회 재검증
- 재검증 실패 시 즉시 401
- 백그라운드 prefetch는 선택, 요청 경로 블로킹 최소화

## 오류 모델 표준

- `TOKEN_MISSING`
- `TOKEN_MALFORMED`
- `TOKEN_SIGNATURE_INVALID`
- `TOKEN_EXPIRED`
- `TOKEN_ISSUER_MISMATCH`
- `TOKEN_AUDIENCE_MISMATCH`
- `TOKEN_KID_NOT_FOUND`

모든 오류는 민감정보 없이 구조화 로그를 남긴다.

## 코드리뷰 집중 포인트

- 클레임 추출 전에 서명 검증이 수행되는가
- `jku`/`x5u` 등 외부 키 URL 헤더를 신뢰하지 않는가
- `aud`를 와일드카드로 허용하지 않는가
- clock skew가 과도하지 않은가
- 예외 발생 시 임시 허용 경로가 없는가
- 모듈 우회(직접 decode) 코드가 없는가

## 언어별 구현 권장

- Python(FastAPI): 공통 dependency 또는 middleware 패키지화
- Node(NestJS/Express): guard/middleware + shared package
- 테스트는 "유효/만료/잘못된 kid/잘못된 issuer/잘못된 audience" 최소 5종 세트 고정

## 근거 문헌

- Keycloak OIDC endpoints: https://www.keycloak.org/securing-apps/oidc-layers
- Keycloak token local validation: https://www.keycloak.org/securing-apps/oidc-layers#_validating_access_tokens
- OIDC Discovery 1.0: https://openid.net/specs/openid-connect-discovery-1_0.html
- RFC 9068 (JWT Profile for OAuth 2.0 Access Tokens): https://datatracker.ietf.org/doc/html/rfc9068
- RFC 8725 (JWT BCP): https://datatracker.ietf.org/doc/html/rfc8725
