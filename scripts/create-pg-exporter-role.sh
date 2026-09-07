#!/usr/bin/env bash
#
# postgres-exporter 가 쓸 read-only 계정을 DB 세 곳에 만든다.
#
#   ./scripts/create-pg-exporter-role.sh
#
# .env 의 PG_EXPORTER_PASSWORD 를 읽는다. 없으면 만드는 방법을 알려 주고 끝낸다.
# 이 스크립트는 .env 를 읽기만 한다. 값을 만들고 적는 것은 사람이 한다.
# 이미 계정이 있으면 비밀번호만 갱신한다. 여러 번 돌려도 된다.

set -Eeuo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO/.env"
ROLE="sandol_exporter"

# 컨테이너명:superuser:db
TARGETS=(
  "meal-service-db:postgres:meal_service"
  "keycloak-db:keycloak:keycloak"
  "sandol-notice-notification-db:root:notice"
)

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *)         echo "알 수 없는 옵션: $1  (--help 참고)" >&2; exit 1 ;;
  esac
  shift
done

[ -f "$ENV_FILE" ] || { echo "'.env' 가 없다: $ENV_FILE" >&2; exit 1; }

PASSWORD="$(grep -E '^PG_EXPORTER_PASSWORD=' "$ENV_FILE" | head -1 | cut -d= -f2- || true)"

if [ -z "$PASSWORD" ]; then
  # 값을 직접 찍지 않는다. 찍으면 그 값이 정해진 것으로 오해할 수 있다.
  # hex 를 쓰는 이유는 이 값이 URL 과 SQL 을 거치기 때문이다.
  cat >&2 <<'EOF'
PG_EXPORTER_PASSWORD 가 .env 에 없다. 아래 순서로 채운다.

  1. 값을 만든다
       openssl rand -hex 24

  2. .env 에 추가한다. 위 출력값을 그대로 붙여 넣는다
       PG_EXPORTER_PASSWORD=<1번 출력값>

  3. 이 스크립트를 다시 실행한다

값은 .env 안에서만 관리한다. 이 스크립트는 .env 를 읽기만 한다.
EOF
  exit 1
fi

fail=0
for t in "${TARGETS[@]}"; do
  IFS=: read -r container superuser db <<< "$t"

  if ! docker inspect "$container" >/dev/null 2>&1; then
    echo "  건너뜀  $container (컨테이너 없음)"
    fail=1
    continue
  fi

  # 비밀번호는 SQL 문자열에 직접 넣지 않고 psql 변수로 넘긴다.
  if docker exec -i "$container" psql -v ON_ERROR_STOP=1 \
       -U "$superuser" -d "$db" -v pw="$PASSWORD" >/dev/null <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$ROLE') THEN
    CREATE ROLE $ROLE LOGIN;
  END IF;
END
\$\$;
ALTER ROLE $ROLE WITH PASSWORD :'pw';
GRANT pg_monitor TO $ROLE;
GRANT CONNECT ON DATABASE "$db" TO $ROLE;
SQL
  then
    echo "  완료    $container ($db)"
  else
    echo "  실패    $container ($db)"
    fail=1
  fi
done

exit "$fail"
