# 산돌이 챗봇 프로젝트 API 문서

## 개요

이 문서는 산돌이 챗봇 프로젝트에서 제공하는 API 엔드포인트 개발 방법을 설명합니다. 이 문서는 FastAPI의 OpenAPI 통합 및 **kakao-chatbot** 라이브러리 사용 방법에 대한 가이드를 제공합니다.

---

## FastAPI 통합 및 OpenAPI 문서화

### `create_openapi_extra` 사용하기

FastAPI는 OpenAPI(Swagger) 문서를 생성하기 위해 엔드포인트에 추가 메타데이터를 제공할 수 있습니다. `create_openapi_extra` 함수는 다음과 같은 요청 페이로드 스키마를 생성합니다:

- **`detail_params`**: 사용자 입력 세부 정보를 설명하는 매개변수.
- **`client_extra`**: 클라이언트별 정보.
- **`contexts`**: 사용자 세션에 대한 컨텍스트 정보.
- **`utterance`**: 예시 사용자 입력.

#### `create_openapi_extra` 예제

다음은 `create_openapi_extra` 함수 사용 템플릿입니다:

```python
from utils import create_openapi_extra

@meal_api.post(
    "/example",
    openapi_extra=create_openapi_extra(
        detail_params={
            "example_param": {
                "origin": "example_value",
                "value": "example_value",
            },
        },
        client_extra={
            "client_key": "example_key",
        },
        utterance="예시 발화",
    ),
)
async def example_endpoint(payload: Payload = Depends(parse_payload)):
    """
    `create_openapi_extra`를 사용하는 예제 엔드포인트입니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화

    - OpenBuilder:
        - 블럭: "예제 블럭"
        - 스킬: "예제 스킬"

    - Params:
        - detail_params:
            - example_param(sys.constant): 예제 매개변수.
        - client_extra:
            - client_key: 클라이언트별 키.
    ---

    Return:
        JSON 응답.
    """
    # 엔드포인트 로직
    return JSONResponse({"message": "예제 응답"})
```

### Docstring 가이드라인

FastAPI는 docstring을 사용하여 OpenAPI 문서를 생성합니다. docstring에는 다음 내용이 포함되어야 합니다:

1. **목적**: 엔드포인트의 기능을 간략히 설명합니다.
2. **카카오 챗봇 연결 정보**:
   - **동작방식**: 발화 또는 버튼 연결로 구분됩니다.
   - **OpenBuilder**: 해당 엔드포인트와 연결된 블럭 및 스킬의 이름을 명시합니다.
   - **Params**:
     - `detail_params`: 카카오톡 챗봇 관리자 센터의 파라미터 설정 정보를 작성합니다.
     - `client_extra`: 블럭 연결 시 제공되는 추가 정보를 작성합니다.
3. **반환값**: 응답 내용을 설명합니다.

#### Docstring 예제

```python
"""
업체 등록을 승인하는 API 입니다.

## 카카오 챗봇 연결 정보
---
- 동작방식: 버튼 연결

- OpenBuilder:
    - 블럭: "업체 등록 승인"
    - 스킬: "업체 등록 승인"

- Params:
    - detail_params:
        - place(sys.constant): 교내 또는 교외
    - client_extra:
        - identification: 식당 ID
---

Return:
    JSON 응답.
"""
```

#### utils.py와 같은 일반 함수
- 일반 함수에도 docstring을 작성하여 다른 개발자가 함수의 사용법을 이해할 수 있도록 합니다. 단, 카카오 챗봇 연결 정보는 작성하지 않으며, Google 스타일의 docstring을 사용합니다.

- **Google 스타일의 docstring**은 다음과 같은 형식을 따릅니다:

```python
def example_function(param1: int, param2: str) -> bool:
    """
    함수의 기능을 간략히 설명합니다.

    Args:
        param1: 매개변수1에 대한 설명.
        param2: 매개변수2에 대한 설명.

    Returns:
        함수의 반환값에 대한 설명.
    """
```

---

## Kakao-Chatbot 라이브러리 통합

`meal.py` 및 `utils.py` 파일에서는 **kakao-chatbot** 라이브러리를 광범위하게 사용합니다. 이 라이브러리는 Kakao OpenBuilder와의 상호작용을 용이하게 합니다.

### 공식 문서

`kakao-chatbot`라이브러리의 자세한 사용법은 [Kakao Chatbot Documentation](https://kakao-chatbot.readthedocs.io/)을 참조하세요.

카카오 챗봇이 반환할 수 있는 다양한 응답 형식을 지원합니다. 이러한 응답 형식은 위 공식문서와 [카카오톡 챗봇 API 가이드](https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format)를 참조하여 구현할 수 있습니다.

### 주요 구성 요소

1. **Payload 파싱**: 사용자 입력 세부 정보를 추출합니다.
    여기서 `parse_payload` 함수는 FastAPI의 `Depends`를 사용하여 Kakao Chatbot Payload를 파싱할 수 있도록 `api_server.utils` 모듈에 구현되어 있는 함수입니다.

   ```python
   from kakao_chatbot import Payload
   payload: Payload = Depends(parse_payload)
   ```

2. **응답 생성**: Kakao Chatbot 응답을 생성합니다.

   ```python
   from kakao_chatbot.response import KakaoResponse, SimpleTextComponent

   response = KakaoResponse()
   response.add_component(SimpleTextComponent("안녕하세요, Kakao!"))
   return JSONResponse(response.get_dict())
   ```

3. **ItemCard와 Carousel**: 복잡한 응답 형식을 구성합니다.

   ```python
   from kakao_chatbot.response.components import ItemCardComponent, CarouselComponent

   item_card = ItemCardComponent([])
   item_card.add_item(title="점심", description="맛있는 식사")

   carousel = CarouselComponent()
   carousel.add_item(item_card)
   ```

#### 예제: 식단 정보 관리

```python
@meal_api.post(
    "/register/restaurant",
    openapi_extra=create_openapi_extra(
        detail_params={
            "name": {"origin": "식당 이름", "value": "예제 식당"},
        },
    ),
)
async def register_restaurant(payload: Payload = Depends(parse_payload)):
    """
    새로운 식당을 등록합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화

    - OpenBuilder:
        - 블럭: "식당 등록"
        - 스킬: "식당 등록"

    - Params:
        - detail_params:
            - name(sys.constant): 식당 이름
    ---

    Return:
        등록 결과를 포함한 JSON 응답.
    """
    response = KakaoResponse()
    response.add_component(SimpleTextComponent("식당이 성공적으로 등록되었습니다."))
    return JSONResponse(response.get_dict())
```

---

## 개발자 노트

1. **임시 데이터**: `create_openapi_extra`에 설정된 값들은 플레이스홀더이며, 실제 데이터로 교체해야 합니다.
2. **에러 처리**: `meal_error_response_maker`를 사용하여 에러 응답을 생성하세요.
3. **테스트**: Swagger UI(`/docs`) 또는 Kakao OpenBuilder를 사용하여 엔드포인트를 검증하세요.

