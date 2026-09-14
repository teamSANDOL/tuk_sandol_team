# sandol_meal_web 기능 명세

작성일: 2026-07-27
최종 갱신: 2026-07-27 (산돌 디자인 가이드 v0.1 리디자인 적용)
기준 커밋: `sandol_meal_web` @ `5c5ed7e` + 리디자인 작업분

> **갱신 요약** — 3장에서 "구현 가능"으로 분류했던 항목 중 백엔드 API가 이미
> 존재하던 A1·A2·A3·A4·A5·A7·A8·A9·A10과 C7이 리디자인과 함께 구현되었습니다.
> 남은 항목은 3.2(백엔드 확장 필요)와 3.3(품질 개선)입니다.

## 1. 개요

`sandol_meal_web`은 학식 서비스의 **관리자 / 식당주용 운영 콘솔**이다. 자체 DB를 갖지 않고
Keycloak으로 로그인한 뒤 `sandol_meal_service` API를 서버 사이드에서 호출하는 BFF
(Backend-For-Frontend)로 동작한다.

| 항목 | 값 |
| --- | --- |
| 프레임워크 | FastAPI + Jinja2 (SSR) |
| 프런트엔드 | Tailwind/daisyUI 프리빌드 CSS (`app/static/css/app.css`) + `ops-overrides.css` + htmx (`hx-boost`) |
| 인증 | Keycloak OIDC Authorization Code + PKCE |
| 세션 저장소 | diskcache `FanoutCache` (`.cache/sessions`, 8 shard) |
| 외부 의존 | `sandol_meal_service` (HTTP, `X-User-ID` 헤더 전달) |
| 배포 경로 | `root_path=/meal-web`, 정적 자산 `/meal-web/static/...` |
| 포트 | 5800 (uvicorn) |
| Node.js 빌드 | 없음 (CSS는 커밋된 프리빌드 산출물) |

### 신뢰 경계

meal-web은 Keycloak 토큰을 검증한 뒤 **자체 서버 세션만 유지**하고, meal-service에는
액세스 토큰이 아니라 `X-User-ID: <keycloak sub>` 헤더만 전달한다. 즉 meal-service는
meal-web을 신뢰된 내부 호출자로 취급한다. 이 헤더가 외부에서 직접 주입되지 않도록
게이트웨이 레벨에서 차단되어야 한다.

---

## 2. 구현된 기능

### 2.1 인증 · 세션 (`app/routers/auth.py`, `app/services/session_service.py`)

| 기능 | 상세 |
| --- | --- |
| 로그인 시작 | `GET /auth/login` — nonce·code_verifier 생성 후 Keycloak authorization endpoint로 302 |
| PKCE | S256 code challenge 사용 |
| 콜백 처리 | `GET /auth/callback` — code/state 검증, 토큰 교환, nonce 검증, `sub` 추출 |
| state 1회성 | `pop_login_state()`로 소비 → 콜백 리플레이 차단, TTL 600초 |
| code/state 누락 | 로그인 플로우 재시작(302)으로 폴백 |
| 세션 생성 | 서버 사이드 세션(`user_id`, `roles`, `csrf_token`, `expires_at`, `token_metadata`) |
| 세션 쿠키 | HttpOnly, `secure`/`samesite` 환경변수 제어, max-age = 토큰 만료까지 |
| 역할 추출 | access token 클레임에서 realm/client role 추출 |
| 로그아웃 | `POST /auth/logout` — 로컬 세션 삭제 + Keycloak `end_session` 리다이렉트 (`id_token_hint` 포함) |
| 권한 판정 | `global_admin`(realm) 또는 `meal_admin`(client) 보유 시 admin |
| CSRF | 세션 바인딩 토큰, 모든 POST에서 `secrets.compare_digest` 비교 |

### 2.2 공통 UI 기반

| 기능 | 상세 |
| --- | --- |
| 랜딩 (`GET /`) | 로그인 여부·권한에 따라 owner/admin 바로가기 카드 분기 |
| 헬스체크 | `GET /health` → `{"status": "ok"}` |
| 역할별 내비게이션 | `base.html` — admin/owner 메뉴 분기, 데스크톱·모바일 별도 렌더 |
| 현재 페이지 하이라이트 | `navigation_context()`의 `current_route` 기반 |
| htmx 부분 전환 | `hx-boost` + `hx-select="#page-shell"` + 로딩 인디케이터 |
| 에러 페이지 | 403(권한 없음 / CSRF 실패)은 `error.html` HTML 렌더, API 요청은 JSON |
| 401 처리 | `login_required:<url>` detail을 파싱해 로그인으로 302 |
| 응답 협상 | `Accept: text/html` 또는 `HX-Request` 여부로 HTML/JSON 분기 |
| 에러 메시지 정규화 | meal-service 응답의 `detail`/`message`를 사용자용 한국어 메시지로 변환 |

### 2.3 식당주(owner) 기능 (`app/routers/owner.py`)

| 기능 | 라우트 | 상세 |
| --- | --- | --- |
| 내 등록 요청 목록 | `GET /owner/requests` | meal-service가 제출자 기준으로 필터링 |
| 등록 요청 작성 폼 | `GET /owner/requests/new` | 752줄 대형 폼 (식당명, 유형, 가격, 캠퍼스 내외, 건물, 지도 링크, 위경도, 운영/브레이크/조·브런치·점심·저녁 시간) |
| 등록 요청 제출 | `POST /owner/requests` | 성공 시 상세 페이지로 302, 실패 시 입력값 보존 재렌더 |
| 등록 요청 상세 | `GET /owner/requests/{id}` | 상태, 제출 시각, 검토 시각, 거절 사유 표시 |
| 등록 요청 삭제 | `POST /owner/requests/{id}/delete` | `confirm_delete=true` 체크 필수 |
| 내 식당 목록 | `GET /owner/restaurants` | `owner_user_id` 필터로 소유 식당만 조회 (admin은 전체) |
| 매니저 신청 목록 | `GET /owner/restaurants/{id}/manager-requests` | 카카오봇으로 접수된 신청 확인 |
| 매니저 신청 승인 | `POST /owner/restaurants/{id}/manager-requests/{rid}/approve` | |

**폼 검증 (클라이언트 아닌 `meal_client.py` 서버 검증)**
- 필수: 식당명, 식당 유형, 운영 시간(시작·종료 모두)
- 한식뷔페 유형(`fixed_korean_buffet`, `variable_korean_buffet`)은 1인 가격 필수
- 가격은 1원 이상 양수 정수
- 시간 범위는 시작/종료 중 하나만 입력 시 400
- 위경도는 float 파싱 검증

### 2.4 관리자(admin) 기능 (`app/routers/admin.py`)

**등록 요청 검토**

| 기능 | 라우트 |
| --- | --- |
| 전체 요청 목록 | `GET /admin/requests` |
| 요청 상세 | `GET /admin/requests/{id}` |
| 승인 | `POST /admin/requests/{id}/approve` |
| 거부 | `POST /admin/requests/{id}/reject` — 거부 사유 필수 |

**등록 식당 관리**

| 기능 | 라우트 |
| --- | --- |
| 식당 목록 | `GET /admin/restaurants` |
| 식당 직접 생성 | `GET /admin/restaurants/new`, `POST /admin/restaurants` — 등록 요청 없이 `owner_user_id` 지정해 생성 |
| 식당 수정 | `GET /admin/restaurants/{id}/edit`, `POST /admin/restaurants/{id}/edit` — ID 제외 전 필드 |
| 식당 삭제 | `POST /admin/restaurants/{id}/delete` — `confirm_delete=true` 필수 |
| 매니저 목록/등록/해제 | `GET|POST /admin/restaurants/{id}/managers`, `POST .../managers/delete` |
| 매니저 신청 목록/승인 | `GET /admin/restaurants/{id}/manager-requests`, `POST .../{rid}/approve` |

**식단 관리**

| 기능 | 라우트 | 상세 |
| --- | --- | --- |
| 식단 목록 | `GET /admin/meals` | 20건/페이지, 식당·최종 수정 날짜 범위 필터 |
| 식단 등록 | `GET /admin/meals/new`, `POST /admin/meals` | 식당 드롭다운(전 페이지 순회 수집), 메뉴는 줄바꿈 구분 |
| 식단 수정 | `GET /admin/meals/{id}/edit`, `POST /admin/meals/{id}/edit` | |

식단 목록 구현 특성 (`_load_filtered_meals`):
- meal-service가 정렬을 제공하지 않아 **7일 단위 윈도우를 과거로 스캔**하며 필요한 건수를 채운 뒤
  meal-web에서 `served_date → updated_at → id` 역순 정렬 후 페이지를 잘라낸다.
- 종료일 미지정 시 "오늘 + 1일"부터 역방향 스캔.
- 시작일 > 종료일이면 자동 스왑(`_normalize_date_range`).
- 요청 페이지가 총 페이지를 넘으면 마지막 페이지로 302.
- 필터를 유지하는 첫/이전/다음/마지막 페이지네이션 URL 생성.

### 2.5 라우트 전체 목록

```
GET  /                                                 root
GET  /health                                           health_check
GET  /auth/login                                       login
GET  /auth/callback                                    callback
POST /auth/logout                                      logout

GET  /owner/restaurants                                owner_restaurants_page
GET  /owner/restaurants/{rid}                          owner_restaurant_detail_page
POST /owner/restaurants/{rid}/managers                 add_owner_restaurant_manager          (B3)
POST /owner/restaurants/{rid}/managers/delete          delete_owner_restaurant_manager       (B3)
POST /owner/restaurants/{rid}/manager-requests/{id}/approve  approve_owner_restaurant_manager_request
POST /owner/restaurants/{rid}/manager-requests/{id}/reject   reject_owner_restaurant_manager_request (B1)
POST /owner/manager-requests                           create_manager_request_web
GET  /owner/meals                                      owner_meals_page
GET  /owner/meals/new                                  owner_new_meal_page
POST /owner/meals                                      create_owner_meal
GET  /owner/meals/{meal_id}/edit                       owner_edit_meal_page
POST /owner/meals/{meal_id}/edit                       update_owner_meal
POST /owner/meals/{meal_id}/delete                     delete_owner_meal
GET  /owner/requests                                   owner_requests_page
GET  /owner/requests/new                               new_owner_request_page
POST /owner/requests                                   create_owner_request
GET  /owner/requests/{request_id}                      owner_request_detail_page
POST /owner/requests/{request_id}/delete               delete_owner_request

GET  /admin                                            admin_dashboard_page
POST /admin/meals/sync                                 admin_meal_sync
GET  /admin/requests                                   admin_requests_page
GET  /admin/requests/{request_id}                      admin_request_detail_page
POST /admin/requests/{request_id}/approve              approve_admin_request
POST /admin/requests/{request_id}/reject               reject_admin_request
GET  /admin/restaurants                                admin_restaurants_page
GET  /admin/restaurants/new                            admin_new_restaurant_page
POST /admin/restaurants                                create_admin_restaurant
GET  /admin/restaurants/{rid}                          admin_restaurant_detail_page
GET  /admin/restaurants/{rid}/edit                     admin_edit_restaurant_page
POST /admin/restaurants/{rid}/edit                     update_admin_restaurant
POST /admin/restaurants/{rid}/delete                   delete_admin_restaurant
POST /admin/restaurants/{rid}/managers                 add_admin_restaurant_manager
POST /admin/restaurants/{rid}/managers/delete          delete_admin_restaurant_manager
POST /admin/restaurants/{rid}/manager-requests/{id}/approve  approve_admin_restaurant_manager_request
POST /admin/restaurants/{rid}/manager-requests/{id}/reject   reject_admin_restaurant_manager_request (B1)
GET  /admin/meals                                      admin_meals_page
GET  /admin/meals/new                                  admin_new_meal_page
POST /admin/meals                                      create_admin_meal
GET  /admin/meals/{meal_id}/edit                       admin_edit_meal_page
POST /admin/meals/{meal_id}/edit                       update_admin_meal
POST /admin/meals/{meal_id}/delete                     delete_admin_meal
```

`(B1)` / `(B3)`은 meal-service 확장 전까지 안내 메시지 또는 403이 표시되는 라우트.

---

## 3. 구현 가능한 기능

### 3.1 백엔드 API가 이미 존재하던 것 — ✅ 구현 완료

`sandol_meal_service`에 엔드포인트가 이미 있었고 meal-web 화면만 없던 항목들로,
리디자인과 함께 모두 구현되었다. (A6만 미착수)

| # | 기능 | 사용 meal-service API | 상태 |
| --- | --- | --- | --- |
| A1 | 식단 삭제 | `DELETE /meals/{meal_id}` | ✅ `delete_admin_meal`, `delete_owner_meal` |
| A2 | 식당주·매니저용 식단 관리 화면 | `POST /meals/{restaurant_id}`, `PATCH /meals/{meal_id}`, `GET /meals/restaurant/{id}` | ✅ `/owner/meals` 전체 CRUD |
| A3 | 식단 목록 검색 필터 확장 | `GET /meals?restaurant_name=&meal_type=` | ✅ 관리자 식단 필터 |
| A4 | 식당 목록 검색 필터 | `GET /restaurants/?name=&establishment_type=&is_campus=` | ✅ 관리자 식당 필터 |
| A5 | 매니저 신청 이력 조회 | `GET /restaurants/{id}/manager-requests?status=` | ✅ 대기·승인·거절·전체 탭 |
| A6 | 메뉴 단위 부분 수정/삭제 | `PATCH /meals/{id}/menus`, `DELETE /meals/{id}/menus` | ⬜ 미착수. UI는 칩 편집기이나 제출은 여전히 `menu` 전체 덮어쓰기 |
| A7 | 최신 식단 대시보드 | `GET /meals/latest` | ✅ `/admin` 대시보드 |
| A8 | 식단 강제 동기화 버튼 | `POST /meals/meal_sync` | ✅ 대시보드·식단 목록 |
| A9 | 웹에서 매니저 신청 | `POST /restaurants/{id}/manager-requests` | ✅ `내 식당` 하단 |
| A10 | 식당 상세 조회 화면 | `GET /restaurants/{id}` | ✅ 탭형 상세(정보/매니저/신청), owner·admin 각각 |

### 3.2 백엔드 확장이 함께 필요한 것

| # | 기능 | 필요한 백엔드 작업 | meal-web 현재 상태 |
| --- | --- | --- | --- |
| B1 | **매니저 신청 거절** | meal-service에 승인(`/approval`)만 있고 거절 엔드포인트가 없음. `/rejection` 추가 필요 | 라우트·UI 완비. 404/405를 감지해 "아직 지원하지 않습니다" 안내 표시 |
| B2 | **식당주 본인 식당 정보 수정** | `PATCH /restaurants/{id}`가 admin 권한을 요구. owner 허용 정책 정의 후 확장 | `can_edit=False`로 버튼 숨김. 허용 시 플래그만 전환 |
| B3 | **식당주의 매니저 직접 등록/해제** | `POST`/`DELETE /restaurants/{id}/managers`가 `get_admin_user` 의존 → owner 허용 여부 정책 결정 필요 | 라우트·UI 완비. 현재는 meal-service 403 메시지 노출 |
| B4 | **소유권 이전 워크플로** | 이전 신청 → 신규 소유자 승인 2단계 플로우가 API 레벨에 없음 | 관리자 직접 변경만 제공(상세 화면 `소유자 변경`) |
| B5 | **식단 목록 서버 정렬/필터** | meal-service에 `order_by` + 서버 페이지네이션 추가하면 `load_filtered_meals` 전체를 제거 가능 | 7일 윈도우 스캔 유지(`page_helpers.py`) |
| B6 | 등록 요청 상태별 필터·검색 | `GET /restaurants/requests`에 status 파라미터 없음 | 탭·검색 UI는 제공하되 meal-web에서 클라이언트 필터링 |

### 3.3 플랫폼·품질 개선 (외부 API 불필요)

| # | 항목 | 현재 상태 |
| --- | --- | --- |
| C1 | **테스트 스위트** | 테스트 코드가 전무. pytest + httpx `ASGITransport`로 라우터·CSRF·역할 가드 테스트 추가 가능 |
| C2 | **토큰 갱신(refresh)** | refresh_token을 저장하지 않아 액세스 토큰 만료 = 세션 강제 종료(기본 1시간). 작업 중 폼 입력 유실 위험 |
| C3 | 세션 저장소 공유 | diskcache는 로컬 파일 기반이라 다중 인스턴스 수평 확장 시 세션이 공유되지 않음. Redis 전환 필요 |
| C4 | 플래시 메시지 | 성공/실패 메시지를 URL 쿼리스트링(`?message=`)으로 전달 → 세션 기반 플래시로 대체 가능 |
| C5 | 구조화 로깅 | `sandol-log-manager` 연동 없이 stdout 로깅만 사용 |
| C6 | 감사 로그 | 누가 언제 승인/거부/삭제했는지 화면에서 확인 불가 |
| C7 | 에러 페이지 커버리지 | ✅ 400·403·404·500 모두 `error.html`로 렌더, API 요청은 JSON 유지 |
| C8 | 접근성/폼 UX | 등록 요청 폼은 단계형 UI로 개선됨. 인라인 검증은 미적용 |
| C9 | 다국어 | 전 화면 한국어 하드코딩 |
| C10 | 사용자 표시명 | ✅ meal-service가 신청자(`submitter_profile`)·소유자(`owner_profile`)·매니저(`profile`) 표시명을 TTL 캐시(5분) 기반으로 응답에 포함, meal-web 전 화면 반영 |
| C11 | 매니저 수 집계 | `GET /restaurants/{id}/managers`가 admin 전용이라 식당주 카드의 매니저 수를 채울 수 없음(B3과 함께 해소) |

---

## 4. 알려진 제약

- **관리자 권한 = 전권**: `global_admin`/`meal_admin` 두 역할만 구분하고 식당 단위 세분화 권한은 없다.
- **owner 목록 필터 우회**: `/owner/restaurants`에서 admin 계정은 `owner_user_id` 필터가 빠져 전체 식당이 보인다(의도된 동작, `owner.py:130`).
- **소유권 이전 미지원**: 일반 사용자의 소유권 이전 절차가 API에 없어 관리자 수동 수정만 가능.
- **식단 목록 성능**: 데이터가 늘수록 페이지당 meal-service 호출 횟수가 증가한다(B5 참고).
- **CSS 빌드 파이프라인 부재**: `app.css`는 커밋된 프리빌드 산출물이며 소스 설정(tailwind.config)이 리포지토리에 없다. 디자인 토큰 변경 시 재생성 경로가 불명확.

---

## 5. 우선순위 제안

A1·A2·A3·A4·A5·A7·A8·A9·A10·C7이 완료된 뒤 남은 우선순위.

| 순위 | 항목 | 근거 |
| --- | --- | --- |
| 1 | C1 테스트 스위트 | 인증·CSRF·역할 가드는 회귀 시 보안 사고로 직결. 화면이 2배로 늘어 더 시급해짐 |
| 2 | B1 매니저 신청 거절 | UI는 이미 배포됨. 엔드포인트가 없어 잘못된 신청이 영구히 pending으로 남음 |
| 3 | B3 식당주 매니저 관리 | 식당주 화면의 매니저 탭이 403으로 막혀 있어 반쪽 기능 상태 |
| 4 | C2 토큰 갱신 | 1시간 세션 만료로 인한 작업 유실 방지 |
| 5 | B2 식당주 식당 수정 | 정보 변경 때마다 관리자를 거쳐야 함 |
| 6 | B5 서버 정렬 | 데이터 증가 전 선제 대응, meal-web 복잡도 대폭 감소 |
| 7 | C10 사용자 표시명 | 운영 화면 전반에서 user id 대신 사람이 읽을 수 있는 이름 노출 |
