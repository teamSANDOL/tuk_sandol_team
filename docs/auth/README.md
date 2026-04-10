# 인증 문서 인덱스

이 디렉터리는 산돌이 프로젝트의 인증 설계, 현재 운영 규칙, 향후 도입 예정 항목을 모아둔 공간입니다.

## 현재 운영 기준

- MSA 간 표준 사용자 컨텍스트 헤더는 `X-User-ID`입니다.
- Gateway 경계에서의 JWT/JWKS 직접 검증은 아직 표준으로 도입하지 않았습니다.
- JWKS 관련 문서는 현행 규칙과 함께 읽되, 일부는 도입 예정 항목을 설명합니다.

## 문서 묶음

### 구조 이해

1. [용어 사전](./glossary.md)
2. [인증 기초 가이드](./auth-basics.md)
3. [MSA 서비스간 통신 인증 절차](./auth-msa-communication.md#msa-auth-understanding)
4. [챗봇(Auth-Relay) 인증](./auth-chatbot-auth-relay.md#auth-relay-understanding)
5. [Flutter WebView 인증(Auth-Relay 미사용)](./auth-flutter-webview.md)

### 구현/검증

1. [MSA 서비스간 통신 인증 절차](./auth-msa-communication.md#msa-auth-dev-guide)
2. [챗봇(Auth-Relay) 인증](./auth-chatbot-auth-relay.md#auth-relay-dev-guide)
3. [JWKS 검증 공통 모듈 제작 가이드라인](./jwks-common-module-guideline.md)
4. [JWKS 도입 전 검증 체크리스트](./jwks-validation-checklist.md)

## 권장 읽기 순서

- 처음 이해할 때: `glossary` → `auth-basics` → `auth-msa-communication` → `auth-chatbot-auth-relay`
- 바로 수정할 때: `auth-msa-communication` → `auth-chatbot-auth-relay` → `jwks-*`
