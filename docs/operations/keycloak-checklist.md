# Keycloak 체크리스트

## Realm 기본 설정

- [ ] realm 이름이 `Sandori`로 되어 있음
- [ ] 루트 `.env`의 `SERVICE_DOMAIN` 값이 실제 Keycloak hostname과 일치함
- [ ] 외부 접근 주소가 `KC_SERVER_URL`과 일치함
- [ ] reverse proxy 경로가 `/auth`로 맞춰져 있음

<details>
<summary>설정 방법 보기</summary>

- Keycloak admin console에 로그인합니다.
- realm 선택 화면에서 실제 사용하는 realm 이름이 `Sandori`인지 확인합니다.
- 루트 compose에서는 `SERVICE_DOMAIN` 값이 Keycloak `KC_HOSTNAME`으로 주입됩니다.
- 변수명을 `KC_HOSTNAME`으로 두지 않은 이유는 동일한 도메인 값을 다른 서비스에서도 재사용할 수 있도록 공통 이름으로 관리하기 위해서입니다.
- hostname, external URL, reverse proxy 경로가 현재 운영 도메인과 `/auth` 기준으로 맞는지 확인합니다.

</details>

## 관리자 계정

- [ ] `KEYCLOAK_ADMIN_USERNAME` 설정됨
- [ ] `KEYCLOAK_ADMIN_PASSWORD` 설정됨
- [ ] admin console 로그인 성공 확인

<details>
<summary>설정 방법 보기</summary>

- 루트 `.env`에 `KEYCLOAK_ADMIN_USERNAME`, `KEYCLOAK_ADMIN_PASSWORD`를 넣습니다.
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
