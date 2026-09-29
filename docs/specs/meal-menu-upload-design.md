# 학생식당 엑셀 메뉴 업로드 기능 설계

- 문서 상태: 초안 v0.7
- 작성일: 2026-09-21
- 대상: `sandol_meal_web`, `sandol_meal_service`, 루트 Compose

## 1. 결정 사항

| 항목 | 결정 |
| --- | --- |
| 웹 서비스 | 별도 MSA를 만들지 않고 기존 `sandol_meal_web`에 화면을 추가한다. |
| 파일 형식 | 과거 iBook 엑셀과 동일한 TIP/E동 주간 식단표 구조다. |
| 처리 위치 | 파일 수신·파싱·DB 반영은 기존 파서를 가진 `sandol_meal_service`가 담당한다. |
| 반영 시점 | 업로드 후 즉시 반영하고 완료 후 분석 결과를 표시한다. |
| 권한 | 산돌이 Keycloak 계정과 전용 client role을 사용한다. 기본 역할명은 `meal_uploader`다. |
| 담당자 변경 | Keycloak 역할 회수·할당으로 처리한다. 사용자 ID를 코드에 고정하지 않는다. |
| 원본 보관 | 업로드 원본과 처리 결과를 기간 제한 없이 비공개 저장소에 보관한다. |
| iBook 동기화 | iBook이 PDF로 변경됐으므로 기존 자동 엑셀 동기화는 중지한다. |
| 서비스 간 인증 | Bearer/JWKS 보강은 별도 보안 이슈로 분리하며 이번에는 구현하지 않는다. |

## 2. 배경

현재 `sandol_meal_service`에는 이미 다음 구현이 있다.

- `ExcelMealImporter(path)`
- TIP 학생식당/E동 레스토랑 블록 파싱
- 날짜 집합과 식사 유형 검증
- `(restaurant_id, meal_type_id, date)` 기준 upsert
- 워크북 전체를 하나의 DB transaction으로 commit
- 동시 동기화를 막는 `_sync_lock`

따라서 별도의 import 도메인, staging table, import 전용 DB model을 만들 필요가 없다.
meal-service에 xlsx 업로드 API 하나를 추가하고 기존 파서를 호출하면 된다.

## 3. 목표

- 지정된 담당자만 엑셀을 업로드할 수 있다.
- 드래그 앤 드롭과 OS 파일 선택 창을 모두 지원한다.
- 파일 전체가 유효할 때만 DB에 즉시 반영한다.
- 반영은 전부 성공하거나 전부 rollback된다.
- 처리 후 주차, 식당, 끼니, 날짜, 총 반영 건수와 메뉴를 보여준다.
- 원본 파일과 분석 결과를 기간 제한 없이 보관한다.
- 기존 meal-web 디자인을 최대한 재사용한다.

## 4. 전체 구조

```text
담당자 브라우저
  │  Keycloak 로그인 / 역할 / CSRF
  ▼
sandol_meal_web
  ├─ 업로드 화면
  ├─ meal_uploader 역할 검사
  └─ multipart 파일 전달
       │  X-User-ID: <Keycloak sub>  (현행 계약 유지)
       ▼
sandol_meal_service
  ├─ POST /meals/excel
  ├─ 파일 검증·원본 보관
  ├─ ExcelMealImporter 재사용
  ├─ 전체 workbook transaction
  └─ 분석 결과 반환
       │
       ▼
PostgreSQL meal 테이블
```

### 4.1 책임 분리

| 구성요소 | 책임 |
| --- | --- |
| meal-web | 로그인, role guard, CSRF, drag/drop, 파일 전달, 응답 결과 화면 |
| meal-service | xlsx 수신, 형식 검증, 원본 보관, 기존 파서 실행, DB transaction, 결과 반환 |
| Keycloak | `meal_uploader` 역할 생성·할당·회수 |
| Compose | meal-service 원본 보관용 persistent volume, 자동 동기화 비활성화 설정 |

## 5. 권한과 인증

### 5.1 Keycloak 역할

기본 역할명은 `meal_uploader`이며 `MEAL_UPLOADER_ROLE`로 실제 생성한 역할명과 맞춘다.
Keycloak 역할은 meal-web 로그인에 사용하는 `KC_CLIENT_ID`의 client role로 생성하고,
담당 계정에 할당한다. 담당자 변경 시 이전 계정에서 역할을 회수한 뒤 새 계정에 부여한다.

| 사용자 | 권한 |
| --- | --- |
| `meal_uploader` | 엑셀 업로드와 해당 요청의 결과 확인 |
| `meal_admin` / `global_admin` | 엑셀 업로드와 해당 요청의 결과 확인 |
| 그 외 로그인 사용자 | 메뉴 미노출, 직접 URL 403 |
| 비로그인 사용자 | Keycloak 로그인으로 이동 |

이번 범위에서 역할 검사는 meal-web이 담당한다. meal-service의 업로드 API는 Gateway 공개
경로에 추가하지 않고 Docker 내부 네트워크에서 meal-web만 호출하도록 한다. 기존 `/meal/`
전체 프록시가 업로드 URL도 전달할 수 있으므로 Gateway에서 `/meal/meals/excel`과
`/meal/meals/excel/`을 명시적으로 404 차단한다. 외부 브라우저 업로드 요청은 `/meal-web/`
경로로만 받고 Gateway body 한도를 6MB로 둔다.

### 5.2 별도 보안 이슈

현재 서비스 간 `X-User-ID` 계약은 유지한다. 다음 항목은 이번 구현과 배포에 포함하지
않는다.

- 제안 제목: `[Security] meal-web → meal-service Bearer 전달 및 JWKS 기반 사용자 검증`
- access/refresh token의 서버 세션 보관·갱신
- `Authorization: Bearer` 전달
- meal-service의 JWT 서명·issuer·audience·expiry 검증
- JWT `sub`와 `X-User-ID` 일치 검증
- meal-service의 최종 역할 검증

## 6. meal-service 변경

### 6.1 신규 API

#### `POST /meals/excel`

- 접근: Docker 내부 meal-web 호출 전용
- Content-Type: `multipart/form-data`
- Part: `file`
- 최대 크기: 5MB
- 허용 형식: `.xlsx`
- 성공: `201 Created`

```json
{
  "data": {
    "upload_id": "0199...",
    "status": "completed",
    "file_name": "2026-09-4주차.xlsx",
    "sha256": "9f4a...",
    "period": {
      "start_date": "2026-09-21",
      "end_date": "2026-09-26"
    },
    "summary": {
      "parsed": 30,
      "reflected": 30,
      "restaurants": 2
    },
    "items": [
      {
        "restaurant_id": 1,
        "meal_type": "lunch",
        "date": "2026-09-21",
        "menu": ["쌀밥", "된장찌개"]
      }
    ]
  }
}
```

기존 `upsert_meal()`은 생성 여부만 반환하고 변경 전 메뉴까지 보존하지 않는다. 따라서
1차 분석 결과는 `신규/수정/동일`을 억지로 구분하지 않고 **파싱 건수와 실제 반영된
항목**을 정확하게 보여준다. 상세 diff가 필요해질 때만 별도 조회 로직을 추가한다.

### 6.2 처리 순서

1. `X-User-ID` 존재 여부를 현재 계약대로 확인한다.
2. 확장자, 파일 크기, 빈 파일 여부를 확인한다.
3. `_sync_lock`을 획득해 scheduler/다른 업로드와 동시 실행을 막는다.
4. SHA-256을 계산하고 같은 parser version의 기존 성공 업로드인지 확인한다.
5. 새 파일은 UUID archive 경로에 `original.xlsx`와 `processing` sidecar를 먼저 쓴다.
6. xlsx ZIP 구조·압축 해제 크기를 검증한 다음 임시 경로에서
   `ExcelMealImporter(temp_path).parse()`를 호출한다.
7. TIP/E동 중 하나라도 없거나 날짜가 불일치하면 전체 거부하고 원본은 실패 상태로 남긴다.
8. 기존 `insert_parsed_to_db(db, parsed)`를 호출한다.
9. 기존 함수가 워크북 전체를 한 transaction으로 commit한다.
10. 성공 분석 결과를 sidecar에 기록하고 응답한다.
11. DB 반영 또는 파싱에 실패하면 rollback/실패 sidecar를 기록하고 원본은 보관한다.
12. 임시 파일을 정리한다.

DB와 파일 시스템은 하나의 transaction이 아니므로 DB commit 뒤 완료 sidecar 기록이 실패할
수 있다. 이 경우 API 응답에는 완료 분석 결과가 반환되고 원본은 남는다. 같은 파일 재업로드는
기존 upsert로 안전하게 재반영되지만 중복 기록은 추가될 수 있다.

### 6.3 원본 보관

```text
MEAL_UPLOAD_ARCHIVE_DIR/
└─ 2026/
   └─ 09/
      └─ <upload_id>/
         ├─ original.xlsx
         └─ result.json
```

- 운영에서는 `MEAL_UPLOAD_ARCHIVE_DIR`을 persistent volume에 둔다.
- 원본과 `result.json`은 자동 만료·삭제하지 않는다.
- 실제 파일명으로 경로를 만들지 않고 UUID를 사용한다.
- 원본 파일명은 정제해 metadata에만 저장한다.
- 일반 uploader에게 원본 삭제 기능을 제공하지 않는다.
- volume을 정기 백업과 저장공간 모니터링 대상에 포함한다.
- 저장소 95% 이상이면 신규 업로드를 중단하고 기존 원본은 삭제하지 않는다.

### 6.4 중복 파일

- `sha256 + parser_version`이 같은 성공 `result.json`이 있으면 DB를 다시 쓰지 않고 기존
  결과를 반환한다.
- 이전 시도가 실패했다면 같은 파일 재시도를 허용한다.
- DB의 `(restaurant_id, meal_type_id, date)` 유니크 제약과 upsert도 중복 행 생성을
  방지한다.

### 6.5 오류 계약

HTTP 오류는 기존 FastAPI 패턴의 `{ "detail": "한국어 안내" }`로 반환한다. 내부
`result.json.error_code`는 archive가 생성된 업로드에만 기록한다.

| HTTP | 사용자 안내 | `result.json.error_code` |
| --- | --- | --- |
| 400 | `.xlsx` 파일만 업로드할 수 있음 / 올바른 xlsx 확인 | `invalid_workbook` (archive 생성 후 검증 실패한 경우) |
| 401 | `X-User-ID` 누락 | 기록하지 않음 |
| 413 | 5MB 초과 | 기록하지 않음 |
| 422 | TIP·E동 주간 식단표 형식 확인 | `invalid_workbook` |
| 507 | 원본 파일을 보관할 저장 공간 부족 | 기록하지 않음 |
| 500 | 메뉴 반영 실패, 기존 메뉴 변경 없음 | `excel_apply_failed` |

## 7. 기존 자동 동기화 중지

meal-service의 변경을 작게 유지하면서 PDF 다운로드 시도를 막는다.

1. `MEAL_EXCEL_AUTO_SYNC_ENABLED` 설정 추가
2. 운영 Compose 값은 `false`
3. `main.py` lifespan에서 값이 `true`일 때만 `start_scheduler()` 호출
4. 시작한 경우에만 `stop_scheduler()` 호출
5. meal-web의 기존 `강제 동기화` 버튼 제거

`BookDownloader`, `download_and_save_excel_to_db`, 기존 `/meals/meal_sync`는 1차 배포에서
삭제하지 않는다. 업로드 기능 안정화 후 별도 정리 작업으로 제거한다.

## 8. meal-web 변경

### 8.1 라우트

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/meal-web/uploader/excel` | 업로드 화면 |
| `POST` | `/meal-web/uploader/excel` | CSRF·역할 검사 후 meal-service에 전달 |

POST 응답은 meal-service의 분석 결과를 받아 곧바로 결과 HTML을 렌더한다. 사용자용 이력
조회 API·화면은 1차 범위에 넣지 않는다. 운영 이력은 meal-service의 비공개
`result.json`으로 보존한다.

### 8.2 업로드 화면

기존 `sd-main`, `sd-page-head`, `sd-card`, `sd-btn`, `sd-alert`, `sd-badge`를 재사용한다.

```text
┌────────────────────────────────────────────────────┐
│ 식단 파일 업로드                                      │
│ 학생식당 주간 식단표(.xlsx)를 올려주세요.             │
├────────────────────────────────────────────────────┤
│             엑셀 파일을 여기에 놓으세요               │
│             또는 [파일 선택]                        │
│          .xlsx만 가능 · 최대 5MB                    │
├────────────────────────────────────────────────────┤
│ 선택 파일: 2026-09-4주차.xlsx · 124KB        [제거]  │
│                                  [업로드 및 반영]   │
└────────────────────────────────────────────────────┘
```

- 드롭 영역 클릭·Enter·Space로도 OS 파일 선택 창을 연다.
- 브라우저 보안상 전체 로컬 경로는 받을 수 없으므로 파일명과 크기만 표시한다.
- POST는 기존 session-bound CSRF 토큰을 요구한다.
- `meal_uploader`, `meal_admin`, `global_admin`만 접근할 수 있다.

### 8.3 결과 화면

- 성공/실패 상태
- 파일명, 크기, hash 앞 12자리, 처리 시각
- 제공 시작일·종료일
- TIP/E동별 날짜·끼니별 반영 메뉴
- 전체 파싱·반영 건수
- 날짜·식당·끼니별 실제 반영 메뉴
- 실패 시 `데이터는 변경되지 않았습니다` 안내

추가 확정 버튼은 없다. 성공 결과 화면이 열릴 때는 이미 반영된 상태다.

## 9. 테스트

### 9.1 meal-service

- 정상 xlsx 업로드 → parse → 한 transaction commit
- TIP 또는 E동 누락 시 0건 반영
- 식당별 날짜 불일치 시 0건 반영
- 손상 xlsx, 잘못된 확장자, 5MB 초과 거부
- 빈 셀 skip, `미운영` 유지
- DB 중간 오류 시 전체 rollback
- 동일 hash 성공 파일 멱등 처리
- 동시 업로드 `_sync_lock` 직렬화
- 원본과 result sidecar 영구 저장
- 저장공간 부족 시 DB 반영 전 507
- auto sync flag false/true에 따른 scheduler 시작·종료

### 9.2 meal-web

- 익명 사용자는 로그인으로 이동
- 역할 없는 사용자는 메뉴 미노출 및 직접 URL 403
- uploader/admin 접근 허용
- CSRF 누락·불일치 403
- drag/drop, 파일 선택, 제거, 재선택
- multipart 파일과 `X-User-ID` 전달
- meal-service 오류별 한국어 안내
- 성공 결과 렌더링

### 9.3 통합 검증

- 실제 담당자 계정 역할 부여·회수
- 실제 엑셀 1회 업로드
- 결과 건수와 meal-service 조회 결과 대조
- 카카오 챗봇 표시 메뉴 확인
- 컨테이너 재기동 후 원본·운영 결과 파일 보존
- iBook scheduler 미실행 확인
- public URL, health, 저장공간 지표 확인

## 10. 구현 순서

1. meal-service auto sync flag 추가 및 운영값 `false` 적용
2. meal-service 원본 archive persistent volume 추가
3. `POST /meals/excel` 구현
4. 기존 importer를 이용한 parse·transaction·결과 응답 구현
5. meal-web의 `meal_uploader` role guard 추가
6. drag/drop·파일 선택·응답 결과 UI 추가
7. Keycloak 역할 생성·담당자 할당
8. 실제 파일로 통합 검증

DB migration과 신규 import table 작업은 없다.

## 11. 완료 조건

- [ ] 별도 업로드 MSA를 만들지 않는다.
- [ ] meal-service에는 xlsx 업로드 API 한 개만 추가한다.
- [ ] 기존 `ExcelMealImporter`와 upsert transaction을 재사용한다.
- [ ] 신규 DB table과 migration을 만들지 않는다.
- [ ] iBook 자동 동기화가 실행되지 않는다.
- [ ] 지정된 Keycloak 역할 사용자만 meal-web에서 업로드할 수 있다.
- [ ] drag/drop과 파일 선택을 모두 지원한다.
- [ ] 정상 파일은 업로드 직후 즉시 반영된다.
- [ ] 잘못된 파일은 DB를 변경하지 않는다.
- [ ] DB 오류 시 워크북 전체가 rollback된다.
- [ ] 결과 화면에서 주차·날짜·식당·끼니·메뉴·건수를 확인한다.
- [ ] 원본과 처리 결과가 자동 만료 없이 보관된다.
- [ ] 서비스 간 인증 보강은 별도 이슈로 유지한다.

## 12. 향후 재검토

- 업로드 양식이 여러 종류로 늘면 parser version/registry 도입
- 다중 인스턴스 운영 시 분산 lock과 공유 object storage 도입
- 상세 신규/수정/동일 diff가 필요하면 반영 전 조회 로직 추가
- 서비스 간 인증 이슈 해결 후 meal-service에서도 JWT·역할 최종 검증
