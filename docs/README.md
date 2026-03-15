# 인증 문서 인덱스

이 디렉터리는 산돌이 프로젝트의 인증 규칙을 현재 코드베이스와 목표 아키텍처 기준으로 재정의한 문서 모음입니다.

## 문서 구성

### 인증 구조 이해 파트

인증이 "왜 이렇게 동작하는지"와 시스템 경계를 이해하기 위한 문서 묶음입니다.

1. [용어 사전](./glossary.md)
2. [인증 기초 가이드 (초심자용)](./auth-basics.md)
3. [MSA 서비스간 통신 인증 절차 - 구조 이해 파트](./auth-msa-communication.md#msa-auth-understanding)
4. [챗봇/디스코드 + Auth-Relay 인증 - 구조 이해 파트](./auth-chatbot-auth-relay.md#auth-relay-understanding)
5. [Flutter WebView 인증(Auth-Relay 미사용)](./auth-flutter-webview.md)

### 개발 가이드 파트

인증을 "어떻게 구현/검증할지"를 바로 적용하기 위한 문서 묶음입니다.

1. [MSA 서비스간 통신 인증 절차 - 개발 가이드 파트](./auth-msa-communication.md#msa-auth-dev-guide)
2. [챗봇/디스코드 + Auth-Relay 인증 - 개발 가이드 파트](./auth-chatbot-auth-relay.md#auth-relay-dev-guide)
3. [JWKS 검증 공통 모듈 제작 가이드라인 (도입 예정)](./jwks-common-module-guideline.md)
4. [JWKS 도입 전 검증 체크리스트(코드리뷰/릴리즈 게이트)](./jwks-validation-checklist.md)

## 권장 읽기 순서

현재 운영 기준: MSA 간 `Authorization` 헤더/JWKS 직접 검증은 미도입이며, `X-User-ID` 중심으로 운영한다.

### 1) 구조를 먼저 이해하고 싶은 경우

1. [용어 사전](./glossary.md)
2. [인증 기초 가이드 (초심자용)](./auth-basics.md)
3. [MSA 서비스간 통신 인증 절차 - 구조 이해 파트](./auth-msa-communication.md#msa-auth-understanding)
4. [챗봇/디스코드 + Auth-Relay 인증 - 구조 이해 파트](./auth-chatbot-auth-relay.md#auth-relay-understanding)
5. [Flutter WebView 인증(Auth-Relay 미사용)](./auth-flutter-webview.md)

### 2) 구현/수정 작업을 바로 해야 하는 경우

1. [MSA 서비스간 통신 인증 절차 - 개발 가이드 파트](./auth-msa-communication.md#msa-auth-dev-guide)
2. [챗봇/디스코드 + Auth-Relay 인증 - 개발 가이드 파트](./auth-chatbot-auth-relay.md#auth-relay-dev-guide)
3. [JWKS 검증 공통 모듈 제작 가이드라인 (도입 예정)](./jwks-common-module-guideline.md)
4. [JWKS 도입 전 검증 체크리스트(코드리뷰/릴리즈 게이트)](./jwks-validation-checklist.md)

## 공통 원칙

- MSA 간 사용자 컨텍스트 헤더는 `X-User-ID`를 사용한다 (Keycloak 사용자 식별자 기반).
- Auth-Relay 내부 인증 절차에서는 Keycloak `sub` 클레임을 사용할 수 있다.
- 현재 MSA 인증은 Gateway 경계의 서명 검증 + `X-User-ID` 전달 규약을 기준으로 운영한다.
- Keycloak Access Token의 MSA별 JWKS 직접 검증은 현재 미적용이며 도입 예정 항목으로 관리한다.
- 신규 언어/프레임워크 서비스의 JWKS 공통 모듈 적용은 도입 시점부터 필수로 전환한다.

## 현재 상태 메모

- gateway route 헤더는 `X-User-ID` 기준으로 정리되어 있다.
- 본 문서의 JWKS 관련 규칙은 "도입 목표"이며, 현행 운영 규칙과 구분해 읽어야 한다.
