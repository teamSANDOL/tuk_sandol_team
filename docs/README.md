# 인증 문서 인덱스

이 디렉터리는 산돌이 프로젝트의 인증 규칙을 현재 코드베이스와 목표 아키텍처 기준으로 재정의한 문서 모음입니다.

## 문서 구성

1. [용어 사전](./glossary.md)
2. [인증 기초 가이드 (초심자용)](./auth-basics.md)
3. [MSA 서비스간 통신 인증 절차](./auth-msa-communication.md)
4. [챗봇/디스코드 + Auth-Relay 인증 및 offline_access 저장](./auth-chatbot-auth-relay.md)
5. [Flutter WebView 인증(Auth-Relay 미사용)](./auth-flutter-webview.md)
6. [JWKS 검증 공통 모듈 제작 가이드라인](./jwks-common-module-guideline.md)
7. [필수 검증 체크리스트(코드리뷰/릴리즈 게이트)](./jwks-validation-checklist.md)

## 공통 원칙

- MSA 간 사용자 컨텍스트 헤더는 `X-User-ID`를 사용한다 (`X-User-ID = Keycloak sub`).
- Auth-Relay 내부 인증 절차에서는 Keycloak `sub` 클레임을 사용할 수 있다.
- API Gateway의 사용자 HMAC 검증(`X-Signature`)은 폐기 대상으로 간주한다.
- 각 MSA는 Keycloak Access Token을 [JWKS](./glossary.md#jwks-json-web-key-set)로 직접 검증한다.
- 신규 언어/프레임워크 서비스는 반드시 공통 JWKS 검증 모듈을 통해 검증한다.

## 현재 상태 메모

- 레포에는 `X-User-Sub`/`X-User-ID`가 혼재되어 있으며 게이트웨이 서명 검증 Lua도 남아있다.
- 본 문서는 목표 규칙 문서화 + 점진 마이그레이션 기준서다.
