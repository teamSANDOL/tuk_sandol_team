# Keycloak 체크리스트

> Keycloak 스택은 별도 레포 [teamSANDOL/sandol-auth](https://github.com/teamSANDOL/sandol-auth)로 분리되었습니다. compose·`.env`·백업·전환 절차는 그 레포의 README와 `docs/migration.md`를 기준으로 하고, 이 문서는 realm·프록시 점검 항목으로 남깁니다.

## Realm 기본 설정

- [ ] realm 이름이 `Sandori`로 되어 있음
- [ ] sandol-auth `.env`의 `KC_PUBLIC_URL`이 실제 Keycloak 공개 주소(`https://<도메인>/auth`)와 일치함
- [ ] 외부 접근 주소가 `KC_SERVER_URL`과 일치함
- [ ] reverse proxy 경로가 `/auth`로 맞춰져 있음

<details>
<summary>설정 방법 보기</summary>

- Keycloak admin console에 로그인합니다.
- realm 선택 화면에서 실제 사용하는 realm 이름이 `Sandori`인지 확인합니다.
- sandol-auth compose에서는 `KC_PUBLIC_URL` 값이 Keycloak `KC_HOSTNAME`으로 주입됩니다.
- hostname, external URL, reverse proxy 경로가 현재 운영 도메인과 `/auth` 기준으로 맞는지 확인합니다.

</details>

## 프록시 신뢰 주소

- [ ] `KEYCLOAK_EDGE_SUBNET`(기본 `172.31.255.248/29`)이 호스트 네트워크와 겹치지 않음. `keycloak_edge` 네트워크는 루트 compose가 만들고, sandol-auth의 `KC_PROXY_TRUSTED_ADDRESSES`가 같은 변수를 쓰므로 두 `.env`에서 값을 같게 유지함
- [ ] `keycloak_edge`에는 gateway와 keycloak만 붙이고, 다른 컨테이너를 붙이면 그 컨테이너가 XFF를 위조할 수 있음
- [ ] 게이트웨이는 `keycloak-edge` 별칭(`KEYCLOAK_UPSTREAM` 기본값)으로 접속해 Keycloak이 전용 대역 IP를 보게 함

## 게이트웨이 업스트림과 relay 차단 (TASK-186)

- [ ] 루트 `.env`의 `KEYCLOAK_UPSTREAM`·`AUTH_RELAY_UPSTREAM`은 같은 서버면 비워 둠(기본 `keycloak-edge:8080`, `auth-relay:8000`). 별도 서버면 `<사설IP>:8080`, `<사설IP>:8000`이며 호스트명 대신 IP도 동작함. 바꾼 뒤 gateway 컨테이너 재시작
- [ ] 공개 경로 `POST /relay/issue_login_link`가 404임(인증 없는 서버 간 API라 gateway에서 차단). `/relay/health`·로그인 콜백 등 나머지 `/relay/*`는 그대로 프록시됨
- [ ] 분리 후 kakao-bot의 `AUTH_RELAY_URL`을 `http://<인증 서버 사설IP>:8000/relay`로 바꿈(relay 포트 직접 호출, gateway 경유 아님)
- [ ] 인증 서버 방화벽에서 8080·8000은 메인 서버 IP만 허용, 9000(관리 포트)은 열지 않음. 상세는 sandol-auth `docs/migration.md`

## 관리자 계정

- [ ] `KEYCLOAK_ADMIN_USERNAME` 설정됨
- [ ] `KEYCLOAK_ADMIN_PASSWORD` 설정됨
- [ ] admin console 로그인 성공 확인

<details>
<summary>설정 방법 보기</summary>

- sandol-auth `.env`에 `KEYCLOAK_ADMIN_USERNAME`, `KEYCLOAK_ADMIN_PASSWORD`를 넣습니다(기존 realm이 있으면 부트스트랩 계정은 무시됩니다).
- 컨테이너 기동 후 admin console에 실제로 로그인해 확인합니다.
- dev/default 비밀번호를 그대로 쓰지 않았는지 다시 확인합니다.

</details>

## Client 설정

### `sandol-kakao-bot`

- [ ] client가 존재함
- [ ] confidential client secret을 `sandol_kakao_bot_service/.env`에 복사함
- [ ] callback / login redirect URL이 실제 배포 주소와 일치함

<details>
<summary>설정 방법 보기</summary>

- Keycloak admin console에서 `sandol-kakao-bot` client를 엽니다.
- client secret을 복사해 `KC_CLIENT_SECRET`에 넣습니다.
- 허용된 redirect URI와 callback URL이 실제 `kakao-bot` 운영 URL과 일치하는지 확인합니다.

</details>

### `sandol-meal-service`

- [ ] client가 존재함
- [ ] confidential client secret을 `sandol_meal_service/.env`에 복사함

<details>
<summary>설정 방법 보기</summary>

- Keycloak admin console에서 `sandol-meal-service` client를 엽니다.
- client secret을 복사해 `sandol_meal_service/.env`의 `KC_CLIENT_SECRET`에 넣습니다.

</details>

### auth-relay 관련 client

- [ ] relay 대상 client 항목이 `clients.json` 또는 env-injected secret 방식으로 준비됨
- [ ] env injection 방식이면 `<CLIENT_KEY>__SECRETS` 값이 정확히 설정됨

<details>
<summary>설정 방법 보기</summary>

- auth-relay는 `clients.json`의 client 정의를 읽습니다.
- secret을 파일에 직접 넣지 않을 거면 `<CLIENT_KEY>__SECRETS` 형식 env를 사용합니다.
- 예: `sandol-kakao-bot`이면 `SANDOL_KAKAO_BOT__SECRETS` 형태를 우선 확인합니다.

</details>

## Service Account 확인

### `sandol-meal-service`

- [ ] service account 활성화됨
- [ ] service account user가 실제로 존재함
- [ ] service account `sub`를 `SERVICE_ACCOUNT_SUB`에 복사함

<details>
<summary>설정 방법 보기</summary>

- Keycloak admin console에서 `sandol-meal-service` client의 service account 설정을 확인합니다.
- service account user 상세 화면에서 user id(sub)를 확인합니다.
- 그 값을 `sandol_meal_service/.env`의 `SERVICE_ACCOUNT_SUB`에 넣습니다.

</details>

## Role 확인

- [ ] global admin realm role이 필요 시 존재함
- [ ] meal admin client role이 필요 시 존재함
- [ ] 대상 사용자 / service account에 필요한 role이 부여되어 있음

<details>
<summary>설정 방법 보기</summary>

- realm role과 client role을 각각 확인합니다.
- 운영자가 쓸 사용자, bot, service account에 필요한 role이 실제로 부여됐는지 확인합니다.
- meal-service 권한 테스트에 필요한 admin 사용자와 service account 권한도 같이 점검합니다.

</details>

## 최종 확인

- [ ] 각 `KC_CLIENT_SECRET`가 올바른 서비스 `.env`에 들어감
- [ ] production에서 dev/default 비밀번호를 안 씀
- [ ] 모든 서비스 URL / callback URL이 실제 도메인을 사용함

<details>
<summary>확인 방법 보기</summary>

- client secret이 섞여 들어가지 않았는지 서비스별 `.env`를 비교합니다.
- relay, kakao-bot, meal-service의 Keycloak 관련 값이 실제 realm/client와 일치하는지 다시 확인합니다.
- callback URL, redirect URL, base URL이 gateway 경로와 실제 운영 도메인 기준으로 맞는지 확인합니다.

</details>
