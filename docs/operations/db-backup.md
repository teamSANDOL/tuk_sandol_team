# DB 백업 운영 가이드

모든 DB 백업은 `scripts/db-backup.sh` 하나가 담당합니다. 새 스크립트를 만들 필요가
없고, 주기 백업도 이 스크립트를 정해진 시각에 한 번 더 돌리는 것이 전부입니다.

## 무엇이 백업되는가

| 대상 | 방식 | 결과 파일 |
| --- | --- | --- |
| meal-service-db | `pg_dump -Fc` | `meal_service.dump` |
| notice-notification-db | `pg_dump -Fc` | `notice.dump` |
| keycloak-db | `pg_dump -Fc` | `keycloak.dump` |
| 카카오 봇 SQLite | `sqlite3 .backup` | `kakao_bot_service.db` |

각 DB의 계정과 비밀번호는 서로 다르며, 스크립트가 서비스별 `.env`를 읽기 전용으로
마운트해 직접 꺼내 씁니다. 운영자가 계정을 따로 외울 필요가 없습니다.

결과는 `SANDOL_BACKUP_DIR`(기본값 `$SANDOL_DATA_DIR/backups`) 아래에 UTC 타임스탬프
디렉터리로 쌓입니다.

## 현재 동작: 배포 시 1회

`db-backup` 서비스는 `docker compose up`마다 one-shot으로 돌고, 마이그레이션을
수행하는 서비스들이 그 완료를 기다립니다. 백업이 실패하면 마이그레이션이 시작되지
않습니다. 배포 사고에 대한 방어는 이것으로 충분합니다.

배포와 무관한 사고, 즉 운영 중 데이터 손상이나 실수로 인한 삭제는 이 방식으로
막지 못합니다. 마지막 배포 이후의 변경이 전부 사라집니다.

## 주기 백업 설정

운영 VM에서 crontab에 한 줄을 추가합니다. 매일 04:00 KST에 실행합니다.

```bash
(crontab -l 2>/dev/null; echo '0 19 * * * cd /home/ubuntu/tuk_sandol_team && /usr/bin/docker compose run --rm db-backup >> /home/ubuntu/data/sandol/db-backup.log 2>&1') | crontab -
```

`cron`은 VM 시간대를 따릅니다. UTC로 동작하는 기본 설정이면 19:00 UTC가 04:00 KST이고,
시간대를 KST로 맞춰 두었다면 `0 4 * * *`로 적습니다. `date` 명령으로 먼저 확인하십시오.
경로의 사용자명은 배포 워크플로가 쓰는 값과 같아야 합니다.

설정 후 한 번 손으로 돌려 결과를 확인합니다.

```bash
cd /home/ubuntu/tuk_sandol_team && docker compose run --rm db-backup
```

## 보존 정책 주의

보존 개수는 `BACKUP_KEEP`(기본 10)이며, 배포 백업과 주기 백업이 같은 디렉터리와 같은
정책을 공유합니다. 하루에 배포를 여러 번 하면 그날 배포 백업만으로 10개가 차서 과거
날짜 백업이 밀려납니다.

주기 백업을 켠다면 루트 `.env`에서 보존 개수를 늘리십시오. 30이면 평시 기준 약 한 달
치가 남습니다.

```bash
BACKUP_KEEP=30
```

덤프 한 벌의 크기와 남은 디스크를 먼저 확인하고 값을 정하십시오.

```bash
du -sh /home/ubuntu/data/sandol/backups/* | tail -3 && df -h /
```

## 복원

복원은 자동화되어 있지 않습니다. 대상 DB만 골라 수동으로 되돌립니다.

```bash
docker compose exec -T meal-service-db pg_restore -U postgres -d meal_service --clean --if-exists < /home/ubuntu/data/sandol/backups/<타임스탬프>/meal_service.dump
```

카카오 봇 SQLite는 서비스를 멈추고 파일을 덮어쓴 뒤 다시 띄웁니다.

```bash
docker compose stop kakao-bot-service && cp /home/ubuntu/data/sandol/backups/<타임스탬프>/kakao_bot_service.db /home/ubuntu/data/sandol/kakao-bot/kakao_bot_service.db && docker compose start kakao-bot-service
```

## 한계

- 백업은 VM 안에만 있습니다. 디스크나 인스턴스를 잃으면 백업도 함께 잃습니다. 외부
  보관이 필요하면 별도로 복사 대상을 정해야 합니다.
- 시점 복구(PITR)는 제공하지 않습니다. 마지막 스냅샷 이후 변경은 복구되지 않습니다.
- 복원 절차를 실제로 연습해 본 기록이 없습니다. 복원이 필요한 날 처음 해보는 일이
  되지 않도록 한 번은 시험해 두는 편이 좋습니다.
