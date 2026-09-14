#!/bin/sh
# 마이그레이션 전에 모든 DB 스냅샷을 남긴다.
# db-backup 서비스가 one-shot으로 실행하고, 마이그레이션을 돌리는 서비스들이
# depends_on: service_completed_successfully 로 이 완료를 기다린다.
# 여기서 non-zero로 끝나면 해당 서비스들이 기동되지 않는다(fail-closed).
set -eu

OUT_ROOT="${BACKUP_OUT_DIR:-/backup}"
KEEP="${BACKUP_KEEP:-10}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$OUT_ROOT/$STAMP"

mkdir -p "$DEST"

dump_pg() {
    name="$1"; host="$2"; db="$3"; user="$4"; pass="$5"
    echo "[db-backup] pg_dump $name ($db@$host)"
    PGPASSWORD="$pass" pg_dump -h "$host" -U "$user" -d "$db" -Fc -f "$DEST/$name.dump"
}

# 각 서비스의 .env를 읽기 전용으로 마운트해서 값을 꺼낸다.
# compose 파일에 비밀번호를 평문으로 적지 않고, 루트 .env에 복제하지도 않기 위함이다.
env_of() {
    file="$1"; key="$2"
    [ -f "$file" ] || { echo "[db-backup] $file 없음" >&2; return 1; }
    sed -n "s/^[[:space:]]*$key[[:space:]]*=[[:space:]]*//p" "$file" | tail -1 | tr -d '"'\''\r'
}

# POSTGRES_DB/USER/PASSWORD가 .env에 없으면 DATABASE_URL(scheme://user:pass@host:port/db?query)에서 뽑아낸다.
# ponytail: DATABASE_URL의 퍼센트 인코딩된 비밀번호는 디코딩하지 않는다.
# 그래도 값이 비면 어떤 파일에 무엇이 빠졌는지 알리고 즉시 종료한다(fail-closed).
resolve_pg_conn() {
    file="$1"
    RDB="$(env_of "$file" POSTGRES_DB)"
    RUSER="$(env_of "$file" POSTGRES_USER)"
    RPASS="$(env_of "$file" POSTGRES_PASSWORD)"
    if [ -z "$RDB" ] || [ -z "$RUSER" ] || [ -z "$RPASS" ]; then
        url="$(env_of "$file" DATABASE_URL)"
        if [ -n "$url" ]; then
            rest="$(echo "$url" | sed -r 's#^[A-Za-z0-9+]+://##')"
            [ -n "$RUSER" ] || RUSER="$(echo "$rest" | sed 's#:.*##')"
            [ -n "$RPASS" ] || RPASS="$(echo "$rest" | sed 's#^[^:]*:##; s#@.*##')"
            [ -n "$RDB" ] || RDB="$(echo "$rest" | sed 's#^.*/##; s#?.*##')"
        fi
    fi
    if [ -z "$RDB" ] || [ -z "$RUSER" ] || [ -z "$RPASS" ]; then
        echo "[db-backup] 오류: $file 에서 DB 접속 정보를 찾을 수 없습니다. POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD 를 각각 채우거나, DATABASE_URL(scheme://user:pass@host:port/db) 하나를 채워야 합니다." >&2
        exit 1
    fi
}

resolve_pg_conn /env/meal.env
dump_pg meal_service meal-service-db "$RDB" "$RUSER" "$RPASS"
resolve_pg_conn /env/notice.env
dump_pg notice notice-notification-db "$RDB" "$RUSER" "$RPASS"
dump_pg keycloak keycloak-db \
    keycloak "${KC_DB_USERNAME:?KC_DB_USERNAME 필요}" "${KC_DB_PASSWORD:?KC_DB_PASSWORD 필요}"

# kakao-bot은 SQLite. sqlite3의 온라인 백업 API를 쓰면 기동 중에도 일관된 스냅샷이 나온다.
SQLITE_SRC="${KAKAO_SQLITE_PATH:-/sqlite/kakao_bot_service.db}"
if [ -f "$SQLITE_SRC" ]; then
    if ! command -v sqlite3 >/dev/null 2>&1; then
        apk add --no-cache sqlite >/dev/null 2>&1 || true
    fi
    if command -v sqlite3 >/dev/null 2>&1; then
        echo "[db-backup] sqlite3 .backup kakao_bot_service.db"
        sqlite3 "$SQLITE_SRC" ".backup '$DEST/kakao_bot_service.db'"
    else
        # ponytail: apk 저장소에 못 닿으면 cp로 폴백한다. 복사 중 write가 들어오면
        # 스냅샷이 깨질 수 있다. 여기서 배포를 막는 건 과하다고 판단해 경고만 남긴다.
        # 확실한 스냅샷이 필요하면 kakao-bot-service를 먼저 멈추고 백업해야 한다.
        echo "[db-backup] WARNING: sqlite3 없음 - cp 폴백. 기동 중 write가 있으면 스냅샷이 불완전할 수 있다." >&2
        cp "$SQLITE_SRC" "$DEST/kakao_bot_service.db"
        for ext in wal shm; do
            [ -f "$SQLITE_SRC-$ext" ] && cp "$SQLITE_SRC-$ext" "$DEST/kakao_bot_service.db-$ext"
        done
    fi
else
    echo "[db-backup] WARNING: SQLite 파일 없음: $SQLITE_SRC (최초 기동?)" >&2
fi

# 오래된 백업 정리. 실패해도 배포를 막지 않는다.
cd "$OUT_ROOT" && ls -1d */ 2>/dev/null | sort -r | tail -n "+$((KEEP + 1))" | while read -r old; do
    echo "[db-backup] 보존정책($KEEP) 초과 삭제: $old"
    rm -rf -- "$old" || true
done

echo "[db-backup] 완료 → $DEST"
ls -la "$DEST"
