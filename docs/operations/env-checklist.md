# 환경 변수 체크리스트

## 루트 `.env`

- [ ] `SECRET_KEY`
- [ ] `COMPOSE_PROJECT_NAME`
- [ ] `SERVICE_DOMAIN`
- [ ] `SANDOL_DATA_DIR`
- [ ] `KAKAO_TOKEN_ENCRYPTION_KEY`
- [ ] `KC_DB_USERNAME`
- [ ] `KC_DB_PASSWORD`
- [ ] `KEYCLOAK_ADMIN_USERNAME`
- [ ] `KEYCLOAK_ADMIN_PASSWORD`

<details>
<summary>설정 방법 보기</summary>

- `SECRET_KEY`: `python3 scripts/generate_secrets.py`로 생성한 값을 사용합니다.
- `COMPOSE_PROJECT_NAME`: 기본값 `sandol_team`을 그대로 써도 됩니다.
- `SERVICE_DOMAIN`: Keycloak의 외부 hostname으로 사용할 서비스 공통 도메인입니다. compose가 이 값을 Keycloak `KC_HOSTNAME`으로 주입하며, 변수명을 일반화한 이유는 다른 서비스에서도 같은 도메인 값을 함께 재사용할 수 있게 하기 위해서입니다.
- `SANDOL_DATA_DIR`: 운영용 bind mount 데이터 루트입니다. Ubuntu 서버 기준 `/home/ubuntu/data/sandol` 사용을 권장합니다. `~/data/...` 형태는 Compose에서 경로 확장이 불안정할 수 있어 쓰지 않고, 절대경로를 사용합니다.
- `KAKAO_TOKEN_ENCRYPTION_KEY`: 생성 스크립트 출력값을 그대로 복붙합니다.
- `KC_DB_USERNAME`: 보통 `keycloak` 그대로 사용합니다.
- `KC_DB_PASSWORD`: 생성 스크립트 출력값을 사용합니다.
- `KEYCLOAK_ADMIN_USERNAME`: 보통 `admin` 그대로 사용합니다.
- `KEYCLOAK_ADMIN_PASSWORD`: 생성 스크립트 출력값을 사용합니다.

</details>

## `sandol-auth-relay/.env`

- [ ] `BASE_URL`
- [ ] `JWT_SECRET`
- [ ] `LIT_ISSUER`
- [ ] `LIT_AUDIENCE`
- [ ] `STATE_TTL_SECONDS`
- [ ] `CHATBOT_CALLBACK_TIMEOUT_SECONDS`
- [ ] `RELAY_TO_CHATBOT_HMAC_SECRET`
- [ ] `REDIRECT_ALLOWLIST`
- [ ] `KAKAO_BOT_APP_ID`
- [ ] `KAKAO_WEBHOOK_PRIMARY_ADMIN_KEY`
- [ ] `KAKAO_WEBHOOK_ALLOWED_ADMIN_KEYS`

<details>
<summary>설정 방법 보기</summary>

- `BASE_URL`: 실제 운영 주소 기준으로 `https://도메인/relay` 형태로 입력합니다.
- `JWT_SECRET`: 생성 스크립트 출력값 사용.
- `LIT_ISSUER`, `LIT_AUDIENCE`: 기본값을 유지해도 되지만, 운영 정책이 있으면 맞춰 수정합니다.
- `STATE_TTL_SECONDS`, `CHATBOT_CALLBACK_TIMEOUT_SECONDS`: 기본값 유지 가능.
- `RELAY_TO_CHATBOT_HMAC_SECRET`: 생성 스크립트 출력값 사용.
- `REDIRECT_ALLOWLIST`: 허용할 redirect path prefix를 넣습니다. 기본 `/`면 전체 상대경로 허용입니다.
- `KAKAO_BOT_APP_ID`, `KAKAO_WEBHOOK_PRIMARY_ADMIN_KEY`, `KAKAO_WEBHOOK_ALLOWED_ADMIN_KEYS`: webhook 기능을 쓸 때만 실제 운영 값으로 채웁니다.
- 중요: `RELAY_TO_CHATBOT_HMAC_SECRET`는 kakao-bot의 `RELAY_CLIENT_SECRETS`와 같은 값이어야 합니다.

</details>

## `sandol_kakao_bot_service/.env`

- [ ] `DEBUG`
- [ ] `TIMEZONE`
- [ ] `BASE_URL`
- [ ] `LOGIN_CALLBACK_URL`
- [ ] `LOGIN_REDIRECT_AFTER`
- [ ] `DATABASE_URL`
- [ ] `CACHE_DIR`
- [ ] `AUTH_RELAY_URL`
- [ ] `MEAL_SERVICE_URL`
- [ ] `STATIC_INFO_SERVICE_URL`
- [ ] `NOTICE_SERVICE_URL`
- [ ] `CLASSROOM_TIMETABLE_SERVICE_URL`
- [ ] `KC_SERVER_URL`
- [ ] `KC_CLIENT_ID`
- [ ] `KC_REALM`
- [ ] `KC_CLIENT_SECRET`
- [ ] `TOKEN_ENCRYPTION_KEY`
- [ ] `RELAY_CLIENT_SECRETS`
- [ ] `NONCE_TTL_SECONDS`

<details>
<summary>설정 방법 보기</summary>

- `DEBUG`, `TIMEZONE`, `CACHE_DIR`, `NONCE_TTL_SECONDS`: 기본값 유지 가능.
- `BASE_URL`: 실제 운영 주소 기준 `https://도메인/kakao-bot`.
- `LOGIN_CALLBACK_URL`: `https://도메인/kakao-bot/users/callback`.
- `LOGIN_REDIRECT_AFTER`: 필요할 때만 입력.
- `DATABASE_URL`: 기본 sqlite를 써도 되고 운영 DB를 따로 쓰면 교체합니다.
- `AUTH_RELAY_URL`, `MEAL_SERVICE_URL`, `STATIC_INFO_SERVICE_URL`, `NOTICE_SERVICE_URL`, `CLASSROOM_TIMETABLE_SERVICE_URL`: 현재 compose 네트워크 기준 기본값을 유지하거나, 실제 배포 주소에 맞게 수정합니다.
- `KC_SERVER_URL`, `KC_CLIENT_ID`, `KC_REALM`: Keycloak 설정과 맞춰 입력합니다.
- `KC_CLIENT_SECRET`: Keycloak admin console에서 `sandol-kakao-bot` client secret을 복사합니다.
- `TOKEN_ENCRYPTION_KEY`: 루트 `KAKAO_TOKEN_ENCRYPTION_KEY`와 같은 값 사용.
- `RELAY_CLIENT_SECRETS`: auth-relay의 `RELAY_TO_CHATBOT_HMAC_SECRET`와 같은 값 사용.

</details>

## `sandol_meal_service/.env`

- [ ] `DEBUG`
- [ ] `SERVICE_ACCOUNT_SUB`
- [ ] `TIP_RESTAURANT_ID`
- [ ] `E_RESTAURANT_ID`
- [ ] `MEAL_TYPES_FILE_NAME`
- [ ] `USER_SERVICE_URL`
- [ ] `TIMEZONE`
- [ ] `DATABASE_URL`
- [ ] `KC_SERVER_URL`
- [ ] `KC_LOCAL_URL`
- [ ] `KC_CLIENT_ID`
- [ ] `KC_CLIENT_SECRET`
- [ ] `KC_REALM`
- [ ] `POSTGRES_DB`
- [ ] `POSTGRES_USER`
- [ ] `POSTGRES_PASSWORD`
- [ ] `POSTGRES_HOST`
- [ ] `POSTGRES_PORT`

<details>
<summary>설정 방법 보기</summary>

- `DEBUG`, `TIP_RESTAURANT_ID`, `E_RESTAURANT_ID`, `MEAL_TYPES_FILE_NAME`, `TIMEZONE`: 기본값 유지 가능.
- `USER_SERVICE_URL`: 현재 구조에서 실사용 여부와 무관하게 기본값 유지 가능.
- `DATABASE_URL`: 가장 쉬운 방식은 `.env.example` 값을 복붙한 뒤 비밀번호만 교체하는 것입니다.
- `POSTGRES_*`: `DATABASE_URL`을 쓰더라도 DB 컨테이너와 healthcheck 때문에 같이 맞춰두는 편이 안전합니다.
- `KC_SERVER_URL`: 외부에서 접근하는 Keycloak 주소.
- `KC_LOCAL_URL`: compose 내부 통신용 주소. 기본값 `http://keycloak:8080/auth/` 유지 권장.
- `KC_CLIENT_ID`: 보통 `sandol-meal-service`.
- `KC_CLIENT_SECRET`: Keycloak admin console에서 해당 client secret 복사.
- `SERVICE_ACCOUNT_SUB`: Keycloak의 `service-account-sandol-meal-service` 사용자 sub를 복사합니다.

</details>

## `sandol_notice_notification/.env`

- [ ] `NODE_ENV`
- [ ] `APP_PORT`
- [ ] `POSTGRES_HOST`
- [ ] `POSTGRES_PORT`
- [ ] `POSTGRES_USER`
- [ ] `POSTGRES_PASSWORD`
- [ ] `POSTGRES_DB`
- [ ] `AMQP_URL`
- [ ] `SCHOOL_NOTIFICATION_EXCHANGE`
- [ ] `SCHOOL_NOTIFICATIONS_TOPIC_NOTICE`
- [ ] `SCHOOL_NOTIFICATIONS_TOPIC_NOTICE_DORMITORY`
- [ ] `SCHOOL_NOTIFICATIONS_TOPIC_SHUTTLE_SCHEDULE`

<details>
<summary>설정 방법 보기</summary>

- 이 서비스는 `.env.example`이 약하므로 현재 `.env` 또는 `.env.dev`를 템플릿처럼 보는 게 가장 빠릅니다.
- `NODE_ENV`: 운영이면 `production`, 개발이면 `development`.
- `APP_PORT`: 보통 기존 값 유지.
- `POSTGRES_*`: notice DB 컨테이너와 맞는 값으로 설정.
- `AMQP_URL`: RabbitMQ 접속 주소 형식에 맞게 입력.
- `SCHOOL_NOTIFICATION_EXCHANGE`, `SCHOOL_NOTIFICATIONS_TOPIC_*`: 운영에서 쓰는 exchange/topic 이름을 그대로 유지하거나 메시지 시스템 정책에 맞게 넣습니다.

</details>

## 빠른 일관성 확인

- [ ] 루트 `KAKAO_TOKEN_ENCRYPTION_KEY` == kakao-bot `TOKEN_ENCRYPTION_KEY`
- [ ] auth-relay `RELAY_TO_CHATBOT_HMAC_SECRET` == kakao-bot `RELAY_CLIENT_SECRETS`
- [ ] 각 `KC_CLIENT_SECRET`가 실제 Keycloak client와 일치함
- [ ] `SERVICE_ACCOUNT_SUB`가 실제 meal service account sub와 일치함
- [ ] 루트 `SERVICE_DOMAIN`이 Keycloak 외부 도메인 및 각 서비스의 공개 URL 기준과 일치함
- [ ] 실제 도메인/URL 값이 reverse proxy 경로와 일치함
- [ ] DB 계정 정보가 각 서비스 DB 컨테이너와 일치함

<details>
<summary>확인 방법 보기</summary>

- HMAC secret은 auth-relay와 kakao-bot에서 완전히 같은 문자열이어야 합니다.
- Kakao token encryption key는 루트와 kakao-bot 값이 같아야 합니다.
- `SERVICE_DOMAIN`은 compose에서 Keycloak `KC_HOSTNAME`으로 연결되므로, `KC_SERVER_URL`, gateway route, 외부 공개 URL의 호스트와 함께 확인합니다.
- `KC_CLIENT_SECRET`는 Keycloak admin console의 client 설정 화면에서 다시 확인합니다.
- URL 값은 gateway route와 실제 운영 도메인 기준으로 다시 맞춰봅니다.
- DB 계정은 compose의 DB 컨테이너 env와 서비스 `.env`를 같이 비교합니다.

</details>
