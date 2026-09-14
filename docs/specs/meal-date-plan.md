# 식단 날짜(date) 도입 구현 계획

대상 브랜치: `claude/meal-menu-date-crud-1f9a80`
서브모듈: `sandol_meal_service`(API/DB 주인), `sandol_kakao_bot_service`, `sandol_meal_web`
상태: **계획만. 코드 변경 없음.**

---

## 0. 사전 검증 결과 (모두 실제 코드/데이터로 확인)

### 0-1. 식사 종류 — 아침은 이미 있음, 마이그레이션 불필요

`app/config/meal_types.json`은 최초 커밋(`069f437`)부터 지금까지 4종을 모두 담고 있고, 이 파일을 수정한 커밋은 그 하나뿐입니다.

```json
{"meal_types": ["breakfast", "brunch", "lunch", "dinner"]}
```

`sync_meal_types()`가 매 기동마다 JSON에 있고 DB에 없는 유형을 추가하므로(`app/utils/lifespan.py:19`), 이 앱으로 한 번이라도 부팅한 DB에는 `breakfast`/`brunch` 행이 존재합니다. **meal_type 추가 마이그레이션은 필요 없습니다.**

진짜 공백은 DB가 아니라 양 끝단입니다.

| 지점 | 현재 상태 |
| --- | --- |
| meal-service DB `meal_type` | breakfast/brunch/lunch/dinner 4종 존재 |
| meal-service xlsx 파서 | 중식·석식만 파싱 (`app/services/excel_importer.py:32-42`) |
| meal-web 관리 화면 | 4종 모두 선택 가능 (`app/routers/admin.py:39-42`) |
| 카카오 봇 표시 | **점심·저녁만.** `mealtype_dict = {"lunch": "점심", "dinner": "저녁"}` (`app/utils/meal.py:49`) |

카카오 봇은 `meal_view`에서 lunch/dinner만 분류하고 나머지는 경고 로그 후 버립니다(`app/routers/meal.py:132-143`). `make_meal_card`는 `mealtype_dict[meal.meal_type]`로 직접 인덱싱하므로 breakfast 카드를 만들면 KeyError가 나지만, **호출 경로를 전수 확인한 결과 조식 행이 카드 생성까지 도달하는 경로는 없습니다.**

```
make_meal_cards 호출처 5곳 모두 lunch/dinner로 이미 걸러진 목록을 넘김
  routers/meal.py:145  meal_view        → if/elif로 분류된 lunch, dinner
  routers/meal.py:528  meal_delete_all  → 빈 리스트
  routers/meal.py:665  meal_menu_delete → MealType.lunch/dinner 명시 생성
  routers/meal.py:847  meal_register    → MealType.lunch/dinner 명시 생성
  routers/meal.py:1012 meal_submit      → meal_type == lunch/dinner 필터
```

따라서 **조식을 DB에 넣어도 봇은 깨지지 않습니다.** 유일한 부작용은 `/meal/view` 요청마다 조식 행 수만큼 경고 로그가 쌓이는 것입니다(`app/routers/meal.py:137`). 조식은 사용자에게 보이지 않고 DB와 관리 웹에만 존재합니다.

### 0-2. 저녁 기준 시각 = **19:00 KST** (커밋 이력에서 확인)

현재 코드에는 시각 기준이 없고 `registered_at.date() == today`만 씁니다. 19시 규칙은 커밋 `a022157`(2026-06-05, "학식 조회 정렬과 분기 최적화를 정리")에서 삭제된 이전 구현에 있었습니다.

```python
standard_time = datetime.now(tz=Config.TZ) - timedelta(days=1)
standard_time = standard_time.replace(hour=19, minute=0, second=0, microsecond=0)
...
if meal.updated_at < standard_time:   # 어제 19시 이전 → 지난 메뉴
    bf_standard.append(meal)
else:                                  # 어제 19시 이후 → 현재 메뉴
    af_standard.append(meal)
```

`app/routers/meal.py:79-81`의 "어제 7시" docstring은 이 규칙의 잔재이며 지금 코드와 맞지 않습니다.

규칙을 뒤집으면 곧 백필 공식입니다. **D-1 19:00 이후에 갱신된 메뉴가 D일의 메뉴**이므로:

```
service_date(updated_at) = (updated_at KST).date() + (1일 if 시각 >= 19:00 else 0)
```

19시는 자정 5시간 전이므로 SQL과 파이썬 모두 한 줄로 표현됩니다.

```sql
((updated_at AT TIME ZONE 'Asia/Seoul') + interval '5 hours')::date
```
```python
(updated_at.astimezone(Config.TZ) + timedelta(hours=5)).date()
```

**기준 컬럼은 `updated_at`으로 확정합니다.** 구 봇 규칙도 `updated_at` 비교였습니다. 알려진 부작용 하나를 감수합니다. 당일 10시에 등록한 메뉴를 같은 날 20시에 오타 수정하면 다음 날 메뉴로 밀립니다. 영향 범위는 백필 1회로 끝나며, 잘못 밀린 행은 관리 웹에서 날짜를 고치면 됩니다.

**이 공식은 마이그레이션 백필에만 존재합니다.** 앱 런타임 코드에는 19시 규칙이 들어가지 않습니다. 신규 등록은 `date`를 필수로 받으므로 서버가 날짜를 추론할 일이 없습니다. 상수 `EVENING_CUTOFF_HOUR = 19`는 마이그레이션 파일 안에만 둡니다.

> 참고: 2026-06-05 이후 데이터는 19시 규칙이 없는 상태에서 쌓였습니다. 그래도 "저녁 등록 = 다음 날 메뉴"라는 운영 관행은 그대로이므로 같은 공식을 전 구간에 적용합니다.

### 0-3. xlsx 실제 레이아웃 — 조식 위치 확인, 기존 진단 정정

실제 파일(`sandol_meal_service/tmp/data.xlsx`, `header=None`으로 52×7, `header=0`으로 51×7)을 두 방식으로 읽어 확인했습니다. **이전 검토에서 제가 "고정 슬라이스가 한 줄 어긋난다"고 한 것은 오류였습니다.** 현재 코드는 `header=0`으로 읽으므로 슬라이스가 정확히 맞습니다(6개 요일 모두 검증).

`header=None` 기준 행 구조 (TIP 블록):

| 행 | col0 | col1~6 |
| --- | --- | --- |
| 0 | `◆TIP 학생식당 주간 식단표◆` | |
| 1 | `8월` | `24일 25일 26일 27일 28일 29일(토)` |
| 2 | `조식` | `미운영 미운영 A 미운영 셀프라면코너 미운영` |
| 3 | | `… 셀프라면/밥/김치 …` |
| 4 | `9:00~\n10:00` | (빈칸) |
| 6 | | col1에 `★중•석식 주메뉴 무제한 리필★` |
| 7 | `중식\n11:00\n~\n14:00` | 각 요일 첫 메뉴 |
| 8~12 | | 나머지 메뉴 |
| 14 | `석식\n17:00\n~\n18:50` | 각 요일 첫 메뉴 |
| 15~19 | | 나머지 메뉴 |
| 20 | `**상기 식단은 …**` | |
| 21~ | `◆E동 레스토랑 주간 식단표◆` | 중식(23), 석식(31). **E동에 조식 행 없음** |

확인된 사실:
- **조식은 TIP 블록 2~3행에만 존재**하고, 라벨 행(2행) 자체가 각 요일의 첫 메뉴를 담습니다. 중식·석식과 같은 구조입니다.
- 조식 블록의 끝은 col0이 다시 채워지는 4행(`9:00~10:00` 시간 표기)입니다.
- 현재 파서의 **실제 버그는 두 가지**입니다.
  1. 일요일에 죽습니다. `_get_weekday()`가 7을 반환하는데 열은 0~6뿐이라 `IndexError: single positional indexer is out-of-bounds`. 재현 확인.
  2. 어느 주의 파일이든 "오늘"로 저장합니다. 주 정보를 전혀 읽지 않습니다.
- `★`/`**` 안내 문구는 블록 사이에 있어 라벨 기반 파싱에서는 걸리지 않지만, 방어적으로 필터링 대상에 넣습니다.
- 조식에는 `미운영`, `A` 같은 비메뉴 문자열이 그대로 들어옵니다. `미운영`은 현재도 메뉴 텍스트로 저장되므로 동일하게 둡니다.

---

## 1. 확정된 설계 결정

| 항목 | 결정 |
| --- | --- |
| 날짜 모델 | `meal.date` (KST 기준 제공 날짜) 추가, `(restaurant_id, meal_type_id, date)` UNIQUE |
| 백필 | `updated_at` 기준, 19:00 이후면 다음 날 |
| 중복 행 | **삭제.** 같은 (식당, 식사유형, 날짜)에서 `updated_at` 최신 1건만 유지 |
| 엑셀 vs 수동수정 | **엑셀(최신 데이터) 우선.** 파일 바이트가 바뀐 틱 또는 `force` 호출 시 해당 주 전체를 덮어씀. 그 사이의 수동 수정은 유지됨 |
| 동기화 주기 | **탐색 모드**: 일요일 00:00부터 30분마다. **감시 모드**: 그 주 데이터가 반영되면 6시간마다. 주중 수동 반영은 `POST /meals/meal_sync` |
| 조식 | **이번 범위는 xlsx 파싱 → DB 저장까지만.** 카카오 봇 노출은 후속 과제 |
| 백필 기준 컬럼 | `updated_at` **확정** (`registered_at` 대안은 채택하지 않음) |
| 19시 규칙 적용 범위 | **마이그레이션 백필 전용.** 런타임 기본값으로는 쓰지 않음 |
| 신규 등록의 `date` | **필수 값.** 서버 기본값 없음 (POST·PATCH 모두) |
| 카카오 봇이 보낼 날짜 | **항상 오늘(KST).** 저녁 등록도 오늘 날짜로 저장 |
| `미운영`·`A` 등 비메뉴 문자열 | **그대로 저장.** 중식·석식의 기존 동작과 동일하게 유지 |
| 봇 경고 로그 | **이번 범위에 포함.** 미표시 식사 유형 로그를 `warning` → `debug`로 |

`date`가 필수가 되면서 **카카오 봇 수정이 선택이 아니라 필수**가 됩니다. 현재 봇은 `{meal_type, menu}`만 보내므로(`app/services/meal_service.py:188-191`) 그대로 두면 식단 확정이 전부 422로 실패합니다. 쓰기 경로는 봇과 관리 웹 둘뿐임을 전 서브모듈 grep으로 확인했습니다.

부작용 하나를 감수합니다. 저녁 7시 이후에 다음 날 메뉴를 올리던 사장님의 등록이 이제 오늘 날짜로 저장되어 **그날 메뉴를 덮어씁니다.** 봇에 날짜 선택 단계를 넣으려면 OpenBuilder 블록 추가가 필요하므로 후속 과제로 둡니다.

---

## 2. 단계별 구현 계획

### A단계 — meal-service 스키마와 마이그레이션

**A-1. 모델** `app/models/meals.py`
- `import datetime as dt` 추가 후 `Meal.date: Mapped[dt.date] = mapped_column(Date, nullable=False)`
- `__table_args__`에 `UniqueConstraint("restaurant_id", "meal_type_id", "date", name="meal_restaurant_meal_type_date_unique")` 추가
- 별도 date 인덱스는 만들지 않습니다. 유니크 인덱스가 조회를 커버하고 테이블은 하루 수 행 규모입니다.

**A-2. 마이그레이션** `alembic/versions/<rev>_add_meal_date.py`, `down_revision = "e8b7f31c9a42"` (단일 head 확인함)

모든 데이터 문장은 `op.execute(sa.text(...))`에 리터럴을 넣습니다. 바인드 파라미터와 rowcount 조회는 offline(`--sql`) 모드에서 실패하므로 쓰지 않습니다.

1. `op.add_column("meal", sa.Column("date", sa.Date(), nullable=True))`
2. 백필
   ```sql
   UPDATE meal
   SET date = ((updated_at AT TIME ZONE 'Asia/Seoul') + interval '5 hours')::date
   ```
3. 중복 제거 — 같은 날짜의 최신 1건만 유지
   ```sql
   DELETE FROM meal m USING meal n
   WHERE m.restaurant_id = n.restaurant_id
     AND m.meal_type_id  = n.meal_type_id
     AND m.date          = n.date
     AND (m.updated_at, m.registered_at, m.id) < (n.updated_at, n.registered_at, n.id)
   ```
4. `op.alter_column("meal", "date", nullable=False)`
5. `op.create_unique_constraint("meal_restaurant_meal_type_date_unique", "meal", [...])`

downgrade는 제약·컬럼만 제거하고, docstring에 **삭제된 중복 행은 복구되지 않음**을 명시합니다.

**배포 전 필수**: `meal` 테이블 덤프를 떠 둡니다. 3번은 비가역입니다.
```bash
docker compose exec meal-service-db pg_dump -U postgres -t meal meal_service > meal_backup_$(date +%F).sql
```

Dockerfile ENTRYPOINT가 매 기동마다 `alembic upgrade head`를 실행하므로 배포 시 자동 적용됩니다.

### B단계 — meal-service API

**B-1. 공용 유틸** `app/utils/meals.py`
- 날짜 추론 헬퍼는 만들지 않습니다. `date`가 필수이므로 서버가 "오늘"을 계산할 일이 없습니다. `/latest`의 기준일 기본값에만 `datetime.now(Config.TZ).date()`를 씁니다(19시 보정 없음).
- `apply_date_filter`: `updated_at` → `Meal.date` 기준, 포함(inclusive) 범위로 변경. 형식 오류 400 메시지는 유지.
- `upsert_meal(db, *, restaurant_id, meal_type_id, menu, date) -> tuple[Meal, bool]`: (식당, 유형, 날짜)로 조회 후 있으면 `menu` 갱신, 없으면 삽입. `IntegrityError`는 그대로 전파하고 라우터에서 409로 변환합니다(임포터는 HTTP 컨텍스트가 없으므로).
- **`update_meal_transaction`도 고쳐야 409가 나옵니다.** 현재 `app/utils/meals.py:184`의 `except Exception` 이 모든 예외를 500으로 바꾸므로, 유니크 위반도 500이 됩니다. `except IntegrityError` 절을 그 앞에 두어 롤백 후 409("해당 날짜에 이미 등록된 식단이 있습니다.")로 매핑하고, `sqlalchemy.exc.IntegrityError` import를 추가합니다.
- 유효 메뉴 랭킹 헬퍼 1개: `WHERE date <= 기준일`, `row_number() OVER (PARTITION BY restaurant_id, meal_type_id ORDER BY date DESC, registered_at DESC, id DESC)`. 두 `/latest` 엔드포인트가 공유합니다.
- 기존 `register_meal_transaction`은 호출자가 POST 하나뿐이므로 제거합니다.

**B-2. 스키마** `app/schemas/meals.py`
- `MealRegister`, `MealUpdate`에 **`date: dt.date` (필수, 기본값 없음)**. 누락 시 FastAPI가 422를 반환합니다.
- `MealResponse`, `MealRegisterResponse`에 `date: dt.date`
- `MealEditResponse`는 건드리지 않습니다(소비자 없음: `/menus` 호출처가 봇·웹 어디에도 없음).

**B-3. 라우터** `app/routers/meals.py`

| 엔드포인트 | 변경 |
| --- | --- |
| `GET /meals`, `GET /meals/restaurant/{id}` | start/end가 `date` 기준 포함 범위. `ORDER BY date DESC, registered_at DESC` 추가 |
| `GET /meals/latest`, `GET /meals/restaurant/{id}/latest` | `date` 쿼리 추가(기본 = 오늘 KST, 19시 보정 없음), `date <= 기준일` 중 최신. `/meals/latest`의 start/end는 제거(호출자 없음, grep 확인) |
| `POST /meals/{restaurant_id}` | body에 **`date` 필수**, upsert, 항상 201 유지 |
| `PATCH /meals/{id}` | **`date` 필수** (이미 전체 교체 스키마), 충돌 시 409 |
| 나머지 | 동작 불변 |

### C단계 — xlsx 파서 리라이트 (조식 포함, 주 단위)

`app/services/excel_importer.py` 전면 교체. 공개 진입점 `ExcelMealImporter().insert_to_db(session)`은 유지합니다.

1. **`pd.read_excel(EXCEL_PATH, header=None)` 필수.** 기본값 `header=0`이면 `◆TIP …` 행이 컬럼명으로 사라져 라벨 기반 블록 탐지가 실패합니다.
2. 블록 분리: col0에 `TIP`이 포함된 행부터 `E동` 행 직전까지 = TIP, `E동` 행부터 끝까지 = E동.
3. 날짜 헤더: 블록 내 col0이 `\d+월`인 첫 행. **날짜가 잡히는 첫 열의 (월, 일)로 기준 날짜를 만들고, 이후 열은 연속 일수를 더합니다.** 연도는 오늘과 가장 가까운 것을 고릅니다. 열 헤더의 일 숫자가 계산값과 다르면 그 열은 건너뜁니다. 월·연도 롤오버 분기가 필요 없어집니다.
4. 헤더 파싱 실패 시 `logger.error` 후 **DB 쓰기 없이 종료**. 요일 추정 폴백은 만들지 않습니다(지난주 파일을 이번 주 날짜로 6일치 덮어쓰는 최악 케이스 방지).
5. 식사 블록: col0이 `조식`/`중식`/`석식`으로 시작하는 라벨 행부터, col0이 다시 비어있지 않은 행 직전까지. 라벨 행 자체가 첫 메뉴를 담는다는 점이 핵심입니다. 브런치는 파일에 없으므로 제외.
6. 메뉴 정제: 기존 `clean_menu` + `★`/`**` 시작 문자열 제외. **`미운영`, `A` 같은 비메뉴 문자열은 필터링하지 않고 그대로 저장합니다.** 중식·석식이 이미 그렇게 동작하고 있고, `미운영`은 사용자에게 "오늘 운영 안 함"을 알려주는 유효한 정보입니다.
7. 쓰기: 파싱된 (식당, 식사유형, 날짜, 메뉴)를 **전부** `upsert_meal`로 반영합니다. 엑셀이 최신이므로 기존 행을 덮어씁니다. 메뉴가 빈 열은 건너뜁니다(행을 만들지도, 지우지도 않음).
8. 파싱과 DB 쓰기 분리: `parse_weekly_menus(df, today) -> list[ParsedMeal]`을 순수 함수로 두어 파일 없이 테스트합니다.
9. 파싱된 주에 오늘이 없으면(학교가 새 주 파일을 아직 안 올림) `logger.warning`으로 stale 표시.

> 결과적으로 일요일 IndexError와 "어느 주든 오늘로 저장" 문제가 함께 사라집니다.

### D단계 — 동기화 트리거 (탐색 30분 / 감시 6시간 2단 주기)

**D-1. 대상 주 판정** `app/services/crawler_service.py`
```python
def target_week_monday(today: dt.date) -> dt.date:
    """탐색 대상 주의 월요일. 일요일에는 다음 날(= 다음 주 월요일)을 본다."""
    if today.isoweekday() == 7:                       # 일요일
        return today + dt.timedelta(days=1)
    return today - dt.timedelta(days=today.isoweekday() - 1)
```
"그 주의 데이터가 업데이트됐다"의 판정은 해시가 아니라 **파싱된 날짜 집합이 `target_week_monday`를 포함하는가**로 합니다. 학교가 지난주 파일을 사소하게 고쳐 다시 올려도 탐색 모드가 풀리지 않습니다.

**D-2. 동기화 함수** `download_and_save_excel_to_db(force: bool = False)`

모듈 수준 상태 4개와 락 1개를 둡니다: `_last_file_hash`, `_last_parsed_week_monday`, `_last_synced_week_monday`, `_last_checked_at`, `_sync_lock = asyncio.Lock()`.

**판정 술어는 하나뿐입니다.** 파싱 결과에서 `parsed_week_monday = min(dates) - timedelta(days=min(dates).weekday())`를 계산해 `_last_parsed_week_monday`에 저장하고, 3번·6번 모두 **`_last_parsed_week_monday == target`** 으로만 판단합니다. "파싱 날짜가 target(월요일)을 포함하는가"로 판정하면 월요일이 공휴일이라 화요일부터 시작하는 파일에서 6번이 영영 거짓이 되어 30분 폴링에 고착됩니다(시뮬레이션으로 재현됨).

```
async with _sync_lock:                      # 스케줄러 틱과 /meal_sync 동시 실행 차단
  now    = datetime.now(Config.TZ)
  target = target_week_monday(now.date())
  탐색모드 = (_last_synced_week_monday != target)

  1) force가 아니고 감시모드이며 마지막 확인이 6시간 이내면 → 즉시 종료
  2) 파일 다운로드, _last_checked_at = now
  3) force가 아니고 바이트 해시가 직전과 같으면
       _last_parsed_week_monday == target 이면 _last_synced_week_monday = target  ← ★
       종료 (DB 쓰기 없음)
  4) 해시 갱신, 그 주 전체 파싱, _last_parsed_week_monday = parsed_week_monday
  5) 파싱 결과 전부 upsert (엑셀 우선)
  6) _last_parsed_week_monday == target 이면 _last_synced_week_monday = target → 감시 모드
     아니면 탐색 모드 유지
```

**락이 필요한 이유**: `POST /meals/meal_sync`(`app/routers/meals.py:482`)는 같은 함수를 직접 호출하고, 파일은 고정 경로 `TMP_DIR/data.xlsx`(`crawler_service.py:13`)에 씁니다. 현재 코드와 스케줄러 어디에도 `max_instances`나 락이 없어, 틱과 수동 동기화가 겹치면 파일 동시 쓰기와 모듈 상태 경합, 신규 유니크 제약으로 한쪽 upsert가 IntegrityError를 냅니다. 모듈 수준 `asyncio.Lock` 하나로 끝납니다.

**★ 3번의 캐시 판정은 반드시 필요합니다.** 학교가 토요일에 다음 주 파일을 먼저 올리는 경우를 시뮬레이션해 확인했습니다. 이 줄이 없으면 일요일 00:00에 탐색 모드로 들어간 뒤 해시가 이미 최신이라 3번에서 매번 조기 종료하고, 커버리지를 영영 평가하지 못해 **일주일 내내 30분 폴링**에 갇힙니다.

| 시나리오: 금요일 00:00 시작, 토요일 10:00 선업로드, 7일간 | 다운로드 횟수 |
| --- | --- |
| 3번 캐시 판정 없음 | 248회 (탐색 모드 고착) |
| 3번 캐시 판정 있음 | 28회 (일요일 00:00 즉시 감시 전환) |

(횟수는 시작 시각 가정에 따라 달라지지만 "약 10배, 고착"이라는 결론은 같습니다.)

**해시 스킵과 "엑셀 우선"의 관계**: 3번 때문에 파일 바이트가 바뀌기 전까지는 관리자가 웹에서 고친 TIP/E동 행이 유지됩니다. 엑셀이 이기는 시점은 **파일이 바뀐 틱 또는 `force` 호출**이며, 감시 모드에서는 파일 변경 반영이 최대 6시간 늦어집니다. 이것이 "최신 데이터 우선"의 실제 의미입니다.

**D-3. 스케줄러** `app/jobs/scheduler.py`
- `trigger="cron", minute="0,30"`, timezone `Asia/Seoul`. **잡은 하나만 둡니다.** 30분마다 깨어나되 감시 모드에서는 1번 조건에서 바로 빠져나오므로 실제 다운로드는 6시간에 한 번입니다.
- 일요일 00:00이 지나면 `target`이 다음 주 월요일로 바뀌어 `탐색모드`가 자동으로 참이 됩니다. **별도의 리셋 코드나 두 번째 잡이 필요 없습니다.**
- 학교 서버 요청량: 감시 모드 하루 4회, 탐색 모드 하루 48회. **탐색은 일요일에 한정되지 않습니다.** 학교가 그 주 파일을 끝내 올리지 않으면 48회/일이 그 주 내내 이어집니다(7일 무업로드 시뮬레이션: 336회). 지시된 30분 주기를 그대로 두되, 부담이 되면 "탐색 24시간 경과 후 1시간 간격"으로 완화하는 조건 하나를 추가할 수 있습니다(선택).

**D-4. 상태 지속성**
- 상태는 메모리에만 둡니다. `TMP_DIR`은 볼륨이 아니라 이미지 내부라 파일로 저장해도 컨테이너 재생성 시 사라지므로 이득이 없습니다.
- 재기동 시 상태가 비면 첫 틱에서 1회 다운로드·파싱하고 곧바로 올바른 모드로 수렴합니다.

**D-5. 강제 동기화** `POST /meals/meal_sync` (외부 경로 `/meal/meals/meal_sync`, 관리자 권한)
- `download_and_save_excel_to_db(force=True)`로 호출해 주기·해시와 무관하게 그 주 전체를 다시 씁니다. 이것이 주중 수동 반영 경로입니다.

### E단계 — 카카오 봇 (조식 표시는 제외)

**E-0. `post_meal`이 오늘 날짜를 보냅니다 — 필수 변경.** `app/services/meal_service.py:188-191`

```python
from datetime import datetime          # ← 이 파일에는 아직 없음 (1~9행 import 확인)

request_body = {
    "meal_type": meal_type,
    "menu": menu_items,
    "date": datetime.now(Config.TZ).date().isoformat(),   # ← 추가
}
```

`Config`는 이미 import되어 있고 `Config.TZ`는 `app/config/config.py:85`에 있습니다. 이 한 줄이 없으면 API 배포 순간 모든 사장님의 식단 확정이 422로 실패합니다.

**E-1. 조식 캐러셀은 만들지 않습니다.** `mealtype_dict`도 그대로 둡니다. 위 0-1에서 확인했듯 조식 행이 DB에 있어도 봇은 안전하며, 사용자 화면에는 나타나지 않습니다.

**E-1b. 미표시 유형 로그 하향 (이번 범위 포함).** 유일한 지점은 `app/routers/meal.py:137-142` 한 곳입니다(다른 `logger.warning` 3곳은 식당명 누락 등 무관).

```python
# 현재
        else:
            logger.warning(
                "식단 정보 오류: kakao_id=%s, meal_type=%s",
                ...
# 변경
        else:
            logger.debug(
                "미표시 식사 유형 건너뜀: kakao_id=%s, meal_type=%s",
                ...
```

레벨만 내리지 않고 문구도 바꿉니다. 조식은 오류가 아니라 아직 노출하지 않는 유형이므로, "식단 정보 오류"로 남으면 운영 중 오진을 부릅니다. 조식을 노출하는 후속 작업에서 이 분기 자체가 사라집니다.

**배포 타이밍**: 봇 PR이 파서 PR보다 먼저 나가므로, 조식 행이 처음 생기는 시점에는 이미 로그가 내려가 있습니다.

**E-2. 날짜 인지**
- `app/schemas/meals.py`의 **`MealCard`**에 `date: dt.date | None = None` 추가(`MealResponse`가 상속). 롤링 배포 중 구버전 응답도 견딥니다.
- `make_meal_card` 푸터를 `date` 기준 "M월 D일 X요일 식단"으로 변경. 현재 푸터는 `updated_at`을 쓰는데, 주 단위로 한 번에 upsert하면 같은 메뉴 재기록 시 `updated_at`이 갱신되지 않아 금요일에도 "월요일 1시 업데이트"로 표시되는 회귀가 생깁니다.
- **`date`가 없는 카드의 폴백이 필요합니다.** 등록 미리보기 4곳(`app/routers/meal.py:655, 660, 837, 842`)은 `MealCard(menu=, meal_type=, restaurant_name=)`만으로 만들어 `date`가 `None`입니다. 푸터 계산은 `d = meal.date or normalize_meal_datetime(meal.updated_at).date()`로 둡니다. 생성 지점은 앱·테스트 모두 키워드 인자라 필드 추가 자체는 안전합니다.
- `sort_meals_for_display`: 오늘 판정은 `meal.date == today`(없으면 기존 `registered_at` 폴백), 지난 메뉴 정렬 키는 `(date, registered_at)` 내림차순.

**E-3. docstring 정리**: `app/routers/meal.py:79-81`의 "어제 7시" 설명을 실제 동작으로 갱신.

### F단계 — 관리 웹

- `app/services/meal_client.py`
  - `MealPayload` TypedDict(66~71행)에 `date: str` 추가.
  - `build_meal_payload`: **서버 기본값이 없으므로 웹이 직접 필수 검증합니다.** 빈 값이면 `MealServiceError(BAD_REQUEST, "식단 날짜를 선택해주세요.")`. 302행의 `_required_int`와 같은 꼴로 `_required_date`를 두고 `date.fromisoformat`으로 형식 검증. 서버에 위임하면 사용자에게 불친절한 422 원문이 그대로 보입니다.
  - `create_meal`(658~661행)은 필드를 골라 담으므로 `create_payload`에 `date`를 **명시적으로** 추가. `update_meal`(682~695행)은 `MealPayload` 전체를 보내므로 TypedDict에 넣는 것으로 충분합니다.
- `app/templates/admin/meal_form.html`: `<input type="date" name="date" required>` 추가(라벨 "식단 날짜"), 신규 등록 폼은 오늘로 프리필.
- `app/routers/admin.py`: `_meal_form_values`에 `date`(기존처럼 `meal.get("date", "")`로 읽어 구 API 응답에도 안전), 목록에 "날짜" 열, 필터 라벨을 "식단 시작일/종료일"로. API가 정렬·서버 페이징을 제공하므로 `_load_filtered_meals`의 주 단위 스캔 루프와 `_api_end_date`, `_is_within_date_range`, `_meal_updated_date`를 삭제하고 단일 호출로 단순화.
- `app/templates/admin/meals.html`: "최신 수정순" → "식단 날짜순", 날짜 열 추가.

> **호환성**: 새 웹은 구 API에도 안전합니다. 구 API는 body의 `date`를 무시하고, 목록은 정렬 없이 `date` 열이 비어 보이는 정도로 그칩니다(과도기 허용). 반대로 **구 웹 + 새 API**는 위험합니다. 구 웹 루프(`admin.py:349`)는 총계는 API로 세고 수집은 `updated_at` 로컬 필터로 하는데, `date`가 `updated_at`보다 이틀 이상 앞선 행(주간 파서가 월요일에 쓴 화~토 행)은 총계에는 잡히고 어떤 주간 창에도 들어오지 않아 마지막 페이지에서 무한 루프가 됩니다. 즉 **미래 날짜 행이 생기는 파서 배포 시점에는 새 웹이 이미 떠 있어야 합니다.** 3장의 배포 순서가 이를 보장합니다.

### G단계 — 테스트

meal-service에는 테스트 인프라가 없으므로 함께 만듭니다.

- `pyproject.toml` dev 그룹에 `pytest`, `pytest-asyncio` 추가 후 `uv lock`. **`requirements.txt`는 재생성하지 않습니다** (Dockerfile이 이 파일로 설치하는데 이미 dev 도구가 섞여 있어, 재생성하면 pytest가 운영 이미지에 들어갑니다).
- `[tool.ruff.lint.per-file-ignores]`에 카카오 봇과 동일한 규칙 추가: `"tests/**/*.py" = ["D","S101","PLR2004"]`, `"tests/conftest.py" = ["E402"]`.
- `tests/conftest.py`: `DATABASE_URL=sqlite+aiosqlite:///:memory:`를 app import 전에 설정, `import app.models`(매퍼 등록) 후 `create_all`, User 1 + Restaurant 2 + meal_type 시드.
- **라우터 테스트 앱 구성** — `main.app`을 그대로 쓰면 안 됩니다. `main.py:19-51`의 lifespan이 `ensure_service_account_in_db()`로 Keycloak을 호출합니다. 라우터만 얹은 `FastAPI()`에 `app.dependency_overrides[get_db]`·`[get_current_user]`를 걸고, `TestClient(app)`를 `with` 없이 생성합니다(`with`를 쓰면 lifespan이 실행됨 — 재현 확인). `X-User-ID` 헤더도 반드시 넣습니다. 헤더가 없으면 `get_current_user`가 body 검증보다 먼저 401을 던져 422 테스트가 성립하지 않습니다(재현 확인).
- `tests/test_meal_dates.py`: upsert 생성/교체, 유니크 위반, `date <= 기준일` 랭킹(미래 제외·정확일 우선·과거 폴백), `apply_date_filter` 포함 범위와 역순 입력, **`date` 누락 시 422**(위 구성 전제), **PATCH 날짜 충돌 시 409**(B-1의 `update_meal_transaction` 수정 검증).
- 19:00 백필 경계는 순수 SQL이라 pytest로 덮지 않습니다. 대신 마이그레이션 검증 절차에 넣습니다. 덤프를 복원한 사본 DB에 `alembic upgrade head`를 돌린 뒤 아래로 확인합니다.
  ```sql
  -- 18:59 KST는 당일, 19:00 KST는 다음 날이어야 함
  SELECT id, updated_at AT TIME ZONE 'Asia/Seoul' AS kst, date
  FROM meal ORDER BY updated_at DESC LIMIT 20;
  -- 유니크 제약 위반이 남아 있지 않은지
  SELECT restaurant_id, meal_type_id, date, count(*)
  FROM meal GROUP BY 1,2,3 HAVING count(*) > 1;
  ```
- `tests/test_excel_importer.py`: 실제 레이아웃을 본뜬 DataFrame으로 — 조식/중식/석식 라벨 행이 첫 메뉴로 잡히는지, 조식 블록이 시간 표기 행에서 끝나는지, 석식 블록이 `**상기 식단…`에서 끝나는지, E동에 조식이 없어도 예외가 없는지, 일요일에도 정상 파싱되는지, 헤더 파싱 실패 시 빈 결과인지.
- `tests/test_sync_schedule.py`: `target_week_monday`가 월~토는 그 주 월요일, 일요일은 다음 날을 반환하는지. 그리고 상태 전이 — 지난주 파일이면 탐색 유지, 이번 주 파일이면 감시 전환, 감시 모드에서 6시간 이내 재호출은 다운로드 없이 종료, `force=True`는 해시·주기를 모두 무시. **토요일 선업로드 회귀 테스트**: 토요일에 다음 주 파일이 반영된 뒤 일요일 00:00 첫 틱에서 해시가 그대로여도 감시 모드로 전환되는지(= D-2의 ★ 경로). **월요일 열 없는 파일 회귀 테스트**: 화~토만 있는 주간 파일로도 첫 틱에 감시 모드로 전환되는지(= 판정 술어 통일 검증). **동시 실행 테스트**: 틱과 `force=True` 호출을 `asyncio.gather`로 동시에 넣어도 다운로드·파싱이 직렬화되는지.
- 카카오 봇: `tests/routers/test_meal_view_ordering.py`에 date 기반 버킷 케이스 추가. **조식 행이 섞여 들어와도 200으로 응답하고 카드가 만들어지지 않는지**도 한 건 넣습니다. 기존 3건은 계속 통과해야 합니다.
- 카카오 봇 `tests/services/test_meal_service_post_meal.py`(신규): **`post_meal` 요청 바디에 `date`가 오늘(KST) ISO 문자열로 들어가는지** 한 건. 기존 `tests/routers/test_meal_submit.py:50-68`은 `post_meal` 자체를 가짜로 바꿔 끼우므로 바디를 볼 수 없습니다. `async post(url, json=...)`를 가진 가짜 클라이언트를 넘겨 `json["date"] == datetime.now(Config.TZ).date().isoformat()`을 단언하는 서비스 단위 테스트여야 합니다. 이 테스트가 없으면 E-0 누락을 배포 후에야 알게 됩니다.
- 검증 명령
  ```bash
  uv run --frozen pytest -q
  uv run --frozen ruff check app tests
  DATABASE_URL=postgresql://u:p@localhost/db uv run --frozen alembic upgrade head --sql
  ```

---

## 3. 작업 순서와 PR 분리 제안

배포 메커니즘부터 확인했습니다. 루트 `.github/workflows/GCE_CD4MSA.yml`은 `workflow_dispatch`(수동 트리거)이고, 95행에서 루트의 서브모듈 포인터 기준으로 **전체 스택을 한 번에 `docker compose up -d`** 합니다. 서비스별 부분 배포는 없습니다. 따라서 "PR 하나 머지 → 배포"가 아니라 **"어떤 포인터들이 머지된 상태에서 배포 버튼을 누르는가"**로 순서를 설계해야 합니다.

| 순서 | 범위 | 배포 회차 |
| --- | --- | --- |
| PR 1 | E (봇: `post_meal` 날짜 전송 + 날짜 인지 + 로그 하향) | 1회차 |
| PR 2 | F (관리 웹) | 1회차 |
| PR 3 | A + B + G(meal-service 테스트) | 2회차 |
| PR 4 | C + D (파서·스케줄러) | 2회차 |

각 PR은 서브모듈 포인터 갱신 커밋이 루트 레포에 따라붙습니다.

### 배포 순서 — 소비자를 먼저, API를 나중에. 배포는 두 번

두 소비자는 모두 **구 API에 대해 전방 호환**이라 먼저 올려도 안전합니다. 실제로 확인했습니다.

```
pydantic 2.12.5, MealRegister에 extra 설정 없음 → 기본값 'ignore'
MealRegister.model_validate({'meal_type':'lunch','menu':[...],'date':'2026-09-11'})
  → {'menu': [...], 'meal_type': <MealType.lunch>}   # date는 조용히 무시됨
```

- 새 봇 + 구 API: `date`가 무시될 뿐 기존과 동일하게 동작. 응답 `date` 부재도 `None` 폴백으로 흡수.
- 새 웹 + 구 API: 생성·수정의 `date`는 무시되고, 목록은 정렬 없이 `date` 열이 비어 보임. 크래시 없음(`_meal_form_values`가 `.get()`으로 읽음).

**1회차 배포** — PR 1 + PR 2 포인터가 머지된 상태에서 실행. 사용자 체감 변화 없음.

**2회차 배포** — PR 3 + PR 4 포인터가 머지된 상태에서 실행. 마이그레이션이 돌고 `date`가 필수가 되며 파서가 주간 행을 쓰기 시작합니다. 소비자는 이미 새 버전이라 실패 구간이 없습니다.

**금지 조합**: 구 웹이 떠 있는 상태에서 PR 4(파서)를 배포하는 것. 구 웹의 목록 루프는 미래 날짜 행을 총계에는 세고 어떤 창에서도 수집하지 못해 무한 루프에 빠집니다. 1회차·2회차 순서만 지키면 이 조합은 발생하지 않습니다.

**후속 과제 (이번 범위 밖)**: 카카오 봇 조식 노출. `mealtype_dict`에 `"breakfast": "아침"`을 넣고 `make_meal_cards`를 유형 목록 기반으로 일반화한 뒤 `meal_view`에 아침 캐러셀을 추가하면 됩니다. 데이터는 2회차 배포(PR 4 파서)부터 쌓입니다.

---

## 4. 결정 완료

열려 있던 항목이 모두 확정되어 **남은 결정 사항은 없습니다.** 착수 가능 상태입니다.

| 항목 | 확정 내용 |
| --- | --- |
| 조식 범위 | xlsx 파싱 → DB 저장까지. 봇 노출은 후속 |
| 동기화 주기 | 탐색 30분(일요일 00:00~) / 감시 6시간 |
| 엑셀 vs 수동수정 | 엑셀 우선, 주 단위 덮어쓰기 |
| 중복 행 | 날짜별 최신 1건만 남기고 삭제 |
| 백필 기준 | `updated_at`, 19:00 이후는 다음 날. **백필 전용** |
| 신규 등록 `date` | 필수 값, 서버 기본값 없음 |
| 봇이 보낼 날짜 | 항상 오늘(KST) |
| 비메뉴 문자열 | `미운영`, `A` 등 그대로 저장 |
| 봇 경고 로그 | `warning` → `debug`, 문구도 변경 |
| 배포 순서 | 2회: 1회차 = 봇 + 웹(PR 1·2), 2회차 = API + 파서(PR 3·4). CD는 수동 전체 스택 배포 |

착수 전 유일한 선행 작업은 **A-2의 DB 덤프**입니다. 중복 행 삭제는 비가역입니다.

### 후속 과제로 남기는 것

- 카카오 봇 조식 노출 (`mealtype_dict` + 아침 캐러셀)
- 카카오 봇 날짜 선택 단계. 지금은 항상 오늘로 고정되므로, 저녁에 다음 날 메뉴를 올리던 사장님은 관리 웹을 쓰거나 다음 날 아침에 등록해야 합니다. OpenBuilder 블록 추가가 필요합니다.
