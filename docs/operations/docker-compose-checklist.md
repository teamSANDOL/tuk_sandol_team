# Docker Compose 체크리스트

## 어떤 compose 파일을 사용할지 결정

- [ ] 운영은 `docker-compose.yml` 기준으로 사용할지 결정함
- [ ] 개발은 `docker-compose.dev.yml` 기준으로 사용할지 결정함
- [ ] auth만 따로 볼 때 `docker-compose.auth.yml`을 쓸지 결정함

<details>
<summary>설정 방법 보기</summary>

- 운영 통합 실행은 보통 루트 `docker-compose.yml`을 기준으로 봅니다.
- 개발 중 코드 마운트와 build가 필요하면 `docker-compose.dev.yml`을 씁니다.
- Keycloak/auth-relay만 따로 띄워 확인할 때만 `docker-compose.auth.yml`을 봅니다.
- 이 문서는 compose 파일 선택과 구조 점검용입니다. env 값 채우기는 `./env-checklist.md`에서 관리합니다.
- 운영 데이터 디렉터리 생성 및 초기 파일 이관은 `./production-data-setup.md`를 함께 봅니다.

</details>

## 이미지 / 빌드 경로 확인

- [ ] 각 서비스가 `image:` 기반인지 `build:` 기반인지 확인함
- [ ] 배포할 태그(`TAG`) 사용 여부를 확인함
- [ ] dev compose의 build context가 실제 디렉터리와 일치함

<details>
<summary>설정 방법 보기</summary>

- 운영 compose는 주로 `image: ...:${TAG:-latest}`를 사용합니다.
- dev compose는 `build: ./서비스경로`를 사용하므로 각 경로가 실제 존재하는지 확인합니다.
- 운영 서버에서 사전 빌드 이미지를 쓸지, 서버에서 직접 build할지 먼저 정합니다.

</details>

## 서비스 포함 범위 확인

- [ ] gateway 포함 여부 확인
- [ ] meal-service / kakao-bot / static-info / classroom / notice 포함 여부 확인
- [ ] keycloak / keycloak-db / auth-relay 포함 여부 확인
- [ ] loki / prometheus / alloy / grafana 포함 여부 확인

<details>
<summary>설정 방법 보기</summary>

- 운영에 꼭 필요한 서비스만 올릴지, 모니터링 스택까지 같이 올릴지 먼저 정합니다.
- `docker-compose.yml`은 모니터링까지 같이 포함합니다.
- auth만 따로 점검할 때는 `docker-compose.auth.yml`이 더 가볍습니다.

</details>

## 루트 공통 도메인 env 확인

- [ ] 루트 `.env`에 `SERVICE_DOMAIN`이 설정되어 있음
- [ ] Keycloak 서비스의 `KC_HOSTNAME`이 `${SERVICE_DOMAIN}`으로 연결되어 있음을 인지함
- [ ] 같은 도메인 값을 다른 서비스에서도 재사용할 수 있도록 공통 이름으로 관리 중임을 인지함

<details>
<summary>설정 방법 보기</summary>

- 현재 compose 파일들은 Keycloak 컨테이너의 `KC_HOSTNAME`에 루트 `.env`의 `SERVICE_DOMAIN`을 주입합니다.
- 변수명을 `KC_HOSTNAME`으로 두지 않은 이유는 Keycloak 전용 설정으로 묶지 않고, 다른 서비스들도 같은 서비스 도메인을 재사용할 수 있게 하기 위해서입니다.
- 따라서 도메인 변경 시 Keycloak만 따로 보지 말고, gateway 경로 및 각 서비스의 외부 URL도 함께 점검하는 편이 안전합니다.

</details>

## 포트 노출 확인

- [ ] gateway 외부 포트 확인
- [ ] grafana / prometheus / loki / alloy 노출 포트 확인
- [ ] auth 전용 compose의 `auth-relay` 포트 노출 확인
- [ ] 외부에서 직접 열 필요 없는 서비스가 노출되지 않는지 확인

<details>
<summary>설정 방법 보기</summary>

- 운영에선 보통 gateway만 외부 reverse proxy 뒤에 둡니다.
- monitoring 포트는 외부 공개 여부를 따로 결정해야 합니다.
- `docker-compose.auth.yml`은 `auth-relay`를 `8020:8000`으로 열고 있으니 용도를 인지하고 사용합니다.

</details>

## volume / 데이터 영속성 확인

- [ ] meal DB volume 확인
- [ ] meal-service 파일 마운트 점검 (`student_cafeteria.json`, `meal_types.json`)
- [ ] notice DB volume 확인
- [ ] keycloak DB / keycloak data volume 확인
- [ ] grafana / alloy / loki data volume 확인
- [ ] dev compose에서 bind mount가 의도대로 걸리는지 확인
- [ ] auth-relay `clients.json`와 static-info `school_info.json` bind mount 여부 확인

<details>
<summary>설정 방법 보기</summary>

- 운영 compose는 named volume 위주라 재기동 후 데이터 보존 여부를 확인합니다.
- 운영에서 bind mount하는 운영 데이터 파일은 repo 내부가 아니라 `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}` 아래에서 관리하는 것을 기준으로 봅니다.
- dev compose는 bind mount를 많이 쓰므로 로컬 파일 변경이 컨테이너에 바로 반영되는 구조입니다.
- Keycloak과 각 DB 관련 volume은 특히 삭제하지 않도록 구분해 둡니다.

> 권장 운영 경로 예시
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/auth-relay/clients.json`
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/meal/meal_types.json`
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/meal/student_cafeteria.json`
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/static-info/school_info.json`
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/classroom/lecture_array.json`
> - `${SANDOL_DATA_DIR:-/home/ubuntu/data/sandol}/classroom/buildings.csv`

> `meal-service`의 식사 타입 파일은 기본적으로 `/app/app/config/meal_types.json`을 읽으며,
> 운영에서는 `meal_types.json`만 관리 대상으로 보고, `test_meal_types.json`은 mount 대상에 포함하지 않습니다.
> 다만 현재 코드 경로는 초기 로딩 시점에만 이 파일을 참조하므로 동작 반영은 재기동/재생성 후 확인해야 합니다.

</details>

## depends_on / healthcheck 순서 확인

- [ ] gateway가 핵심 서비스 healthcheck 이후 올라오는지 확인
- [ ] meal-service가 keycloak / meal-service-db 이후 올라오는지 확인
- [ ] notice-notification이 amqp / notice DB 이후 올라오는지 확인
- [ ] keycloak이 keycloak-db 이후 올라오는지 확인
- [ ] healthcheck endpoint/path가 현재 코드와 맞는지 확인

<details>
<summary>설정 방법 보기</summary>

- compose의 `depends_on.condition`이 실제 healthcheck와 연결되는지 봅니다.
- healthcheck path가 바뀌었는데 compose가 예전 path를 보는 경우가 없는지 확인합니다.
- startup 순서 문제는 서비스 장애처럼 보이기 쉬워서, env보다 먼저 compose에서 보는 게 좋습니다.

</details>

## 네트워크 / 서비스명 확인

- [ ] 모든 서비스가 `sandol_network`에 붙는지 확인
- [ ] 내부 URL이 compose 서비스명과 일치하는지 확인
- [ ] `keycloak`, `auth-relay`, `meal-service-db`, `notice-notification-db`, `amqp` 서비스명이 실제 코드 기본값과 맞는지 확인

<details>
<summary>설정 방법 보기</summary>

- 서비스 간 통신은 대부분 compose 서비스명 기반입니다.
- 예를 들어 `http://keycloak:8080`, `http://auth-relay:8000`, `meal-service-db`, `amqp` 같은 이름이 바뀌면 코드 기본값도 같이 맞춰야 합니다.
- 이 체크는 env 값 자체를 보는 게 아니라 compose 네이밍과 내부 DNS가 맞는지 확인하는 단계입니다.

</details>

## reverse proxy / gateway 경로 확인

- [ ] gateway config mount 경로 확인
- [ ] `sandol-gateway/gateway` 디렉터리가 실제 최신 설정인지 확인
- [ ] `/auth`, `/relay`, `/kakao-bot`, `/meal`, `/static-info`, `/classroom-timetable`, `/notice-notification`, `/grafana` 경로를 다시 확인

<details>
<summary>설정 방법 보기</summary>

- compose는 gateway 설정 디렉터리를 그대로 마운트합니다.
- 따라서 실제 운영에선 gateway repo의 route 파일이 최신인지가 중요합니다.
- 서비스 URL 문제가 날 때 env보다 gateway route가 먼저 어긋난 경우가 많으니 분리해서 확인합니다.

</details>

## auth 전용 compose 주의사항

- [ ] `docker-compose.auth.yml`의 하드코딩된 admin/keycloak 비밀번호 인지함
- [ ] 운영에서는 auth 전용 compose를 그대로 쓰지 않을지 판단함
- [ ] auth 전용 compose가 dev/테스트용인지 명확히 구분함

<details>
<summary>설정 방법 보기</summary>

- `docker-compose.auth.yml`에는 `admin/admin`, `keycloak/keycloak` 같은 값이 파일에 직접 들어 있습니다.
- 운영용이라면 이 파일을 그대로 쓰지 말고, 최소한 root env 기반 compose로 정리해야 합니다.
- 이 체크는 secret 생성이 아니라 compose 파일 자체의 안전성 점검입니다.

</details>

## 로깅 / 모니터링 스택 확인

- [ ] `logging.driver=local` 정책 유지 여부 확인
- [ ] loki / prometheus / alloy / grafana를 같이 올릴지 결정함
- [ ] grafana subpath(`/grafana`) 관련 설정 확인

<details>
<summary>설정 방법 보기</summary>

- 운영 초기에 서비스만 먼저 올리고, 모니터링은 나중에 붙일 수도 있습니다.
- grafana는 subpath 기준 설정이 들어 있으니 reverse proxy와 맞는지 확인합니다.
- 로그 적재까지 같이 할지, 최소 기능만 먼저 올릴지 compose 단계에서 결정합니다.

</details>

## 실제 실행 전 최종 확인

- [ ] 사용할 compose 파일 조합이 정리됨
- [ ] 불필요한 서비스가 제외됐는지 확인
- [ ] named volume / bind mount 전략 확인
- [ ] healthcheck / depends_on / 네트워크 / 포트 확인 완료
- [ ] env 체크리스트와 compose 체크리스트를 따로 완료함

<details>
<summary>확인 방법 보기</summary>

- env 값 채우기는 `./env-checklist.md`에서 끝냅니다.
- compose 구조 점검은 이 문서에서 끝냅니다.
- 둘을 섞지 않고 따로 확인해야 어디서 문제가 나는지 빨리 찾을 수 있습니다.

</details>
