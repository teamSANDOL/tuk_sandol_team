# 용어 사전

## Access Token

리소스 서버(MSA API)에 접근할 때 `Authorization: Bearer <token>`으로 전달하는 단기 토큰.

## Refresh Token

만료된 Access Token을 재발급받기 위한 토큰. 유출 시 영향이 크므로 저장/로그 정책이 더 엄격해야 한다.

## offline_access

사용자 세션이 없어도 백엔드가 장기적으로 토큰 갱신을 수행할 수 있게 하는 OIDC 스코프.

## OIDC (OpenID Connect)

OAuth 2.0 위에서 사용자 인증 정보를 표준화한 프로토콜.

## PKCE

Authorization Code 탈취 공격 완화를 위한 확장. `code_verifier`/`code_challenge`를 사용한다.

## Authorization Code Flow

사용자 브라우저를 통해 인가 코드를 받고 서버가 토큰 교환을 수행하는 인증 플로우.

## Token Exchange

기존 토큰(subject token)을 입력으로 받아 다른 대상(audience)용 토큰으로 교환하는 절차.

## JWT

서명된 클레임 토큰 포맷. Header/Payload/Signature 3부분으로 구성된다.

## Claim

JWT payload의 필드(예: `iss`, `aud`, `exp`, `sub`, `realm_access.roles`).

## sub

OIDC 표준 사용자 식별자 클레임. 인증 경계(Auth-Relay, 로그인 콜백 처리)에서 주로 사용한다.

## X-User-ID

산돌이 MSA 내부 사용자 컨텍스트 전달용 표준 헤더. 값은 Keycloak `sub`를 그대로 사용한다.

## JWKS (JSON Web Key Set)

토큰 서명 검증용 공개키 집합 문서. 보통 OIDC discovery의 `jwks_uri`로 접근한다.

## kid

JWT header의 키 식별자. JWKS에서 어떤 공개키를 선택할지 결정할 때 사용한다.

## issuer (`iss`)

토큰 발급자 식별자. 서비스는 사전에 허용한 issuer와 정확히 일치하는지 검증해야 한다.

## audience (`aud`)

토큰 대상자. 해당 MSA가 자신에게 발급된 토큰인지 판단할 때 사용한다.

## Clock Skew

시스템 시간 오차. `exp`/`nbf`/`iat` 검증 시 제한된 허용치(예: 60~180초)를 둔다.

## Fail Closed

검증 실패 시 요청을 허용하지 않는 보안 원칙. "임시 허용"은 금지한다.

## Replay Attack

이전 정상 요청을 재전송해 부정 처리하는 공격. `nonce`, timestamp 검증으로 완화한다.
