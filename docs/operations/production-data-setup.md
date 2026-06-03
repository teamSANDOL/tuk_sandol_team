# 운영 데이터 디렉터리 준비 가이드

이 문서는 Ubuntu 운영 서버에서 `docker-compose.yml`이 사용하는 운영 데이터 디렉터리를 준비하는 방법을 정리합니다.

운영 compose는 repo 내부 파일이 아니라 아래 경로를 기준으로 bind mount 합니다.

- 기본 경로: `/home/ubuntu/data/sandol`
- compose 변수: `SANDOL_DATA_DIR`

> `~/data/...` 형태는 Docker Compose에서 경로 확장이 불안정할 수 있으므로 사용하지 않습니다.
> 운영에서는 항상 절대경로를 사용합니다.

## 1. 사전 조건

- Ubuntu 서버에 `ubuntu` 사용자로 접속 가능한 상태
- 운영 repo가 서버에 이미 clone 되어 있는 상태
- 운영에서 사용할 루트 `.env`에 `SANDOL_DATA_DIR=/home/ubuntu/data/sandol`가 설정되어 있는 상태

예시:

```env
SANDOL_DATA_DIR=/home/ubuntu/data/sandol
```

## 2. 디렉터리 트리 생성

아래 명령으로 운영 데이터 디렉터리를 만듭니다.

```bash
mkdir -p /home/ubuntu/data/sandol/auth-relay
mkdir -p /home/ubuntu/data/sandol/kakao-bot
mkdir -p /home/ubuntu/data/sandol/log-manager/loki
mkdir -p /home/ubuntu/data/sandol/meal
mkdir -p /home/ubuntu/data/sandol/static-info
mkdir -p /home/ubuntu/data/sandol/classroom
```

한 번에 만들고 싶으면:

```bash
mkdir -p \
  /home/ubuntu/data/sandol/auth-relay \
  /home/ubuntu/data/sandol/kakao-bot \
  /home/ubuntu/data/sandol/log-manager/loki \
  /home/ubuntu/data/sandol/meal \
  /home/ubuntu/data/sandol/static-info \
  /home/ubuntu/data/sandol/classroom
```

권한을 `ubuntu` 기준으로 정리하려면:

```bash
chown -R ubuntu:ubuntu /home/ubuntu/data
chmod -R u+rwX,go-rwx /home/ubuntu/data/sandol
```

### Loki 로그 저장소 권한 주의

Loki bind mount를 `${SANDOL_DATA_DIR}/log-manager/loki:/var/lib/loki` 형태로 쓰는 경우,
호스트 소유자가 `root` 또는 `ubuntu`인 것만으로는 충분하지 않을 수 있습니다.
공식 Loki 컨테이너는 기본적으로 `UID 10001`로 실행될 수 있으므로,
`/var/lib/loki`에 매핑된 호스트 디렉터리를 이 UID가 쓸 수 있어야 합니다.

예시:

```bash
mkdir -p /home/ubuntu/data/sandol/log-manager/loki
chown -R 10001:10001 /home/ubuntu/data/sandol/log-manager/loki
chmod -R 755 /home/ubuntu/data/sandol/log-manager
```

`mkdir /var/lib/loki/chunks: permission denied` 오류가 보이면,
대부분 이 디렉터리 권한 또는 소유자 설정 문제로 봅니다.

## 3. 초기 파일 이관

아래 예시는 repo 루트에서 실행하는 기준입니다.

### auth-relay

```bash
cp ./sandol-auth-relay/app/config/clients.json \
  /home/ubuntu/data/sandol/auth-relay/clients.json
```

### kakao-bot

운영에서는 SQLite DB 파일을 bind mount 합니다.

```bash
touch /home/ubuntu/data/sandol/kakao-bot/kakao_bot_service.db
chmod 600 /home/ubuntu/data/sandol/kakao-bot/kakao_bot_service.db
chown ubuntu:ubuntu /home/ubuntu/data/sandol/kakao-bot/kakao_bot_service.db
```

### meal

```bash
cp ./sandol_meal_service/app/config/meal_types.json \
  /home/ubuntu/data/sandol/meal/meal_types.json

cp ./sandol_meal_service/app/config/student_cafeteria.json \
  /home/ubuntu/data/sandol/meal/student_cafeteria.json
```

### static-info

```bash
cp ./sandol-static-info-service/app/config/school_info.json \
  /home/ubuntu/data/sandol/static-info/school_info.json
```

### classroom

```bash
cp ./sandol_classroom_timetable_service/data/lecture_array.json \
  /home/ubuntu/data/sandol/classroom/lecture_array.json

cp ./sandol_classroom_timetable_service/data/buildings.csv \
  /home/ubuntu/data/sandol/classroom/buildings.csv
```

## 4. 권장 최종 파일 구조

```text
/home/ubuntu/data/sandol/
├── auth-relay/
│   └── clients.json
├── kakao-bot/
│   └── kakao_bot_service.db
├── log-manager/
│   └── loki/
├── meal/
│   ├── meal_types.json
│   └── student_cafeteria.json
├── static-info/
│   └── school_info.json
└── classroom/
    ├── lecture_array.json
    └── buildings.csv
```

## 5. 운영 반영 전 확인

파일이 다 들어갔는지 확인합니다.

```bash
ls -R /home/ubuntu/data/sandol
```

루트 `.env`에 값이 있는지도 확인합니다.

```bash
grep '^SANDOL_DATA_DIR=' .env
```

compose가 실제로 이 경로를 해석하는지 확인합니다.

```bash
docker compose -f docker-compose.yml config
```

출력에서 아래와 비슷한 source 경로가 보이면 정상입니다.

- `/home/ubuntu/data/sandol/auth-relay/clients.json`
- `/home/ubuntu/data/sandol/kakao-bot/kakao_bot_service.db`
- `/home/ubuntu/data/sandol/log-manager/loki`
- `/home/ubuntu/data/sandol/meal/meal_types.json`
- `/home/ubuntu/data/sandol/static-info/school_info.json`
- `/home/ubuntu/data/sandol/classroom/lecture_array.json`

## 6. 실제 반영 절차

운영 데이터 파일을 준비한 뒤 compose를 다시 적용합니다.

```bash
docker compose -f docker-compose.yml up -d
```

이미 떠 있는 컨테이너가 파일을 시작 시점에만 읽는 경우가 많으므로, 운영 데이터 변경 후에는 안전하게 재생성/재기동하는 방식으로 봅니다.

예시:

```bash
docker compose -f docker-compose.yml up -d --force-recreate meal-service static-info-service classroom-timetable-service auth-relay
```

## 7. 주의사항

- 운영에서는 `test_meal_types.json`을 관리 대상으로 보지 않고 mount도 하지 않습니다.
- 따라서 운영 환경에서 `MEAL_TYPES_FILE_NAME=test_meal_types.json`처럼 설정하지 않도록 주의합니다.
- 이 데이터 파일들은 대부분 hot reload를 보장하지 않습니다. 운영 반영은 재기동/재생성 기준으로 보는 것이 안전합니다.
- `clients.json`에는 민감한 값이 들어갈 수 있으므로 파일 권한을 엄격하게 유지합니다.
- Loki 저장 디렉터리를 bind mount하는 경우, 컨테이너 실행 UID(예: `10001`)가
  실제로 쓰기 가능한지 확인해야 합니다.
- 운영 파일 수정은 repo 내부가 아니라 `/home/ubuntu/data/sandol` 아래에서 수행해야 합니다.
