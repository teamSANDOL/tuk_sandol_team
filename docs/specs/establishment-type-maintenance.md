# `establishment_type` 유지보수 기준

이 문서는 식당 유형(`establishment_type`) 값이 여러 서비스에 하드코딩되어 있는 위치와, 유형을 추가할 때 필요한 변경 범위를 기록합니다.

## 현재 계약

현재 알려진 canonical 유형은 다음 4가지입니다.

| 값 | 의미 |
| --- | --- |
| `student` | 교내 학생식당 |
| `fixed_menu_restaurant` | 고정메뉴 일반식당 |
| `fixed_korean_buffet` | 고정메뉴형 한식뷔페 |
| `variable_korean_buffet` | 메뉴 변경형 한식뷔페 |

현재 구현은 유형이 삭제되지 않고 기존 목록에 추가만 된다는 것을 전제로 합니다. 따라서 기존 4개 값의 의미와 호환성을 유지해야 하며, 기존 데이터를 다른 값으로 바꾸거나 유형을 제거하는 변경은 별도의 마이그레이션 및 협의 대상입니다.

Kakao의 소비자 계약은 다음과 같습니다.

- meal-service가 새 유형을 반환해도 Kakao는 `str`로 수용합니다.
- 알 수 없는 유형은 일반 식당으로 취급하고 메뉴를 표시합니다.
- 특수 분류 및 표시 순서 변경은 `student`에만 적용합니다.
- 새 유형을 추가해도 Kakao에서 별도 분기를 추가하지 않는 한 기본 메뉴 표시 동작을 유지합니다.

## 유형 추가 시 변경 순서

### 1. Producer: `sandol_meal_service`

새 유형을 생성·수정 API에서 정상적으로 받으려면 다음을 함께 갱신합니다.

| 파일 | 심볼/위치 | 용도 |
| --- | --- | --- |
| `sandol_meal_service/app/schemas/restaurants.py` | `EstablishmentType` | 허용 유형 `Literal` 목록 |
| `sandol_meal_service/app/schemas/restaurants.py` | `ESTABLISHMENT_TYPE_DESCRIPTION` | API 문서용 유형 설명 |
| `sandol_meal_service/app/schemas/restaurants.py` | `BUFFET_ESTABLISHMENT_TYPES`, `RestaurantRequest.validate_price_for_establishment_type` | 뷔페 유형의 가격 필수 조건. 새 유형이 뷔페이면 함께 분류 |
| `sandol_meal_service/app/utils/restaurants.py` | `validate_establishment_type_price` | 서비스 내부 등록·시드 데이터 가격 검증 |
| `sandol_meal_service/app/routers/restaurants.py` | 식당 생성·수정·목록의 `establishment_type` 타입/필터 | HTTP 요청 및 목록 필터 계약 |
| `sandol_meal_service/app/config/student_cafeteria.json` | 시드 항목의 `establishment_type` | 새 유형을 시드 데이터에 사용할 때 갱신 |

유형을 DB 데이터에 적용하는 경우에는 별도 Alembic migration을 작성해야 합니다. 과거 값 변환 migration은 참고용이며 수정하지 않습니다.

### 2. Consumer: `sandol_kakao_bot_service`

일반 메뉴 표시를 위해 새 유형을 추가할 때 Kakao 코드를 수정할 필요는 없습니다. 다음 동작을 유지하는 것이 기준입니다.

| 파일 | 심볼/위치 | 용도 |
| --- | --- | --- |
| `sandol_kakao_bot_service/app/schemas/meals.py` | `RestaurantSchema.establishment_type` | producer의 현재 목록에 고정하지 않고 문자열로 수용 |
| `sandol_kakao_bot_service/app/services/meal_service.py` | `fetch_restaurants` | 식당 유형 필터를 문자열로 전달하고 응답의 새 유형을 파싱 |
| `sandol_kakao_bot_service/app/routers/meal.py` | `meal_view`의 `fetch_restaurants(..., establishment_type="student")` | `student` 식당 ID만 별도로 조회하여 특수 정렬 |
| `sandol_kakao_bot_service/app/utils/meal.py` | `sort_meals_for_display` | 학생식당 ID만 후순위로 정렬하고 나머지 유형은 일반 식당으로 처리 |

새 유형을 `student`처럼 특수 취급해야 한다는 요구가 생길 때만 Kakao의 분류 계약과 테스트를 별도로 변경합니다. 단순히 유형 목록에 추가하는 경우에는 기본 메뉴 표시 경로를 사용합니다.

### 3. Consumer: `sandol_meal_web`

meal-web은 현재 유형 목록을 입력값 검증과 화면 선택지에 하드코딩합니다. 관리자 또는 식당주 화면에서 새 유형을 등록·수정할 수 있어야 한다면 다음 위치를 함께 갱신합니다.

| 파일 | 심볼/위치 | 용도 |
| --- | --- | --- |
| `sandol_meal_web/app/services/meal_client.py` | `EstablishmentType`, `build_restaurant_payload` | API payload 타입과 허용값 검증 |
| `sandol_meal_web/app/services/view_models.py` | `ESTABLISHMENT_TYPE_LABELS` | 화면 표시 라벨 |
| `sandol_meal_web/app/templates/owner/new_request.html` | 유형별 JavaScript 분기 및 라벨 맵 | 식당주 등록 폼의 선택지·가격·메뉴 변경 동작 |
| `sandol_meal_web/app/templates/admin/restaurant_form.html` | 유형 선택지 | 관리자 등록·수정 폼 선택지 |
| `sandol_meal_web/app/templates/admin/restaurants.html` | 필터 선택지 | 관리자 식당 목록 필터 |

새 유형의 가격·메뉴 변경 규칙이 기존 유형과 다르면 `new_request.html`의 조건 분기도 함께 검토합니다. 유형을 단순 라벨로만 추가하는 경우에도 producer API의 허용값과 web의 검증·선택지를 일치시켜야 합니다.

### 참고 문서

다음 문서에도 현재 유형 목록과 유형별 업무 규칙이 설명되어 있으므로, 유형의 의미나 가격 규칙을 바꿀 때 함께 확인합니다.

- `sandol_meal_service/README.md` — meal-service의 유형 정의·판정 원칙·마이그레이션 기준
- `docs/specs/meal-web-feature-spec.md` — meal-web의 한식뷔페 가격 필수 규칙

## 과거 migration과 테스트

다음 migration은 현재 운영 목록을 정의하는 코드가 아니라 과거 값(`vendor`, `external`)을 canonical 값으로 변환한 기록입니다. 새 유형 추가 시 기존 migration을 수정하지 말고 새 migration을 추가합니다.

- `sandol_meal_service/alembic/versions/9c9a6d6a5f1d_update_restaurant_establishment_types.py`
- `sandol_meal_service/alembic/versions/c2d4a8f74f36_rename_vendor_to_fixed_menu_restaurant.py`

회귀 테스트에서 유형 목록이나 Kakao의 unknown type 동작을 직접 고정한 위치도 변경 시 확인합니다.

- `sandol_kakao_bot_service/tests/services/test_meal_service_fetch_restaurants.py`
- `sandol_kakao_bot_service/tests/routers/test_meal_view_ordering.py`

유형을 추가할 때는 최소한 다음을 검증합니다.

1. meal-service가 새 유형을 생성·수정 요청에서 허용하는가
2. meal-web에서 새 유형을 제출할 수 있는가
3. Kakao가 새 유형의 메뉴를 누락하지 않고 표시하는가
4. 새 유형이 의도하지 않게 `student` 특수 정렬 대상이 되지 않는가
