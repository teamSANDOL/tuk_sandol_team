"""학식 관련 API 파일입니다.

학식 관련 API가 작성되어 있습니다.
학식 보기, 등록, 삭제 등의 기능을 담당합니다.
"""

from datetime import datetime, timedelta

from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from kakao_chatbot import Payload, ValidationPayload
from kakao_chatbot.response import (
    KakaoResponse,
    QuickReply,
    ActionEnum,
    ValidationResponse,
)
from kakao_chatbot.response.components import (
    CarouselComponent,
    SimpleTextComponent,
    ItemCardComponent,
    ImageTitle,
)

from api_server.utils import (
    parse_payload,
    create_openapi_extra,
    check_tip_and_e,
    check_access_id,
    split_string,
    make_meal_cards,
    meal_response_maker,
    meal_error_response_maker,
)
from api_server.settings import NAVER_MAP_URL_DICT, logger, BLOCK_IDS
from api_server.payload import Payload as pydanticPayload
from crawler import get_registration, Restaurant, get_meals
from crawler.settings import KST

meal_api = APIRouter(prefix="/meal")


@meal_api.post(
    "/register/restaurant/change_id",
    openapi_extra=create_openapi_extra(
        detail_params={
            "varification": {
                "origin": "test_식당_id",
                "value": "test_식당_id",
            },
        },
        utterance="업체계정변경",
    ),
)
async def register_restaurant_change_id(payload: Payload = Depends(parse_payload)):
    """업체를 관리하는 관리자 ID를 변경하는 API입니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화
        - "업체계정변경"
        - "업체ID변경"

    - OpenBuilder:
        - 블럭: "계정변경"
        - 스킬: "업체ID변경"

    - Params:
        - detail_params:
            - varification(sys.constant): 변경할 업체 ID
    ---

    Returns:
        str: ID 변경 결과를 반환합니다.
    """
    logger.info("식당 ID 변경 요청 수신: user_id=%s", payload.user_id)
    assert payload.detail_params is not None
    varification = payload.detail_params["varification"].origin

    response = KakaoResponse()
    try:
        logger.debug(
            "식당 ID 변경 시도: verification=%s, user_id=%s",
            varification,
            payload.user_id,
        )
        Restaurant.change_identification(varification, payload.user_id)
    except (FileNotFoundError, ValueError) as error:
        logger.error("식당 ID 변경 실패: error=%s", error)
        if str(error) in ("등록된 식당이 없습니다.", "식당을 찾을 수 없습니다."):
            return JSONResponse(
                response.add_component(SimpleTextComponent(str(error))).get_dict()
            )

    logger.debug("변경된 식당 ID 정보 불러오기: user_id=%s", payload.user_id)
    restaurant: Restaurant = Restaurant.by_id(payload.user_id)
    item_card = ItemCardComponent([])
    item_card.image_title = ImageTitle(title=restaurant.name, description="식당 정보")
    item_card.add_item(title="점심 시간", description=restaurant.lunch_time)
    item_card.add_item(title="저녁 시간", description=restaurant.dinner_time)
    item_card.add_item(title="위치", description=restaurant.location)
    item_card.add_item(title="가격", description=f"{restaurant.price_per_person}원")
    item_card.add_button(
        label="메뉴 보기", action="message", message_text=f"학식 {restaurant.name}"
    )
    url = NAVER_MAP_URL_DICT.get(restaurant.name, None)
    if url:
        item_card.add_button(
            label="식당 위치 지도 보기", action="webLink", web_link_url=url
        )
    response.add_component(item_card)
    response.add_component(
        SimpleTextComponent(
            "ID 변경이 완료되었습니다. 이제부터 위 식당의 식단 정보를 관리할 수 있습니다."
        )
    )
    logger.info(
        "식당 ID 변경 완료: user_id=%s, restaurant_name=%s",
        payload.user_id,
        restaurant.name,
    )
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/restaurant/decline",
    openapi_extra=create_openapi_extra(
        detail_params={
            "double_check": {
                "origin": "거절",
                "value": "거절",
            },
        },
        client_extra={
            "identification": "test_식당_id",
        },
    ),
)
@check_access_id("sandol")
async def register_restaurant_decline(payload: Payload = Depends(parse_payload)):
    """업체 등록을 거절하는 api 입니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "업체 등록 거절"
        - 스킬: "업체 등록 거절"

    - Params:
        - detail_params:
            - double_check(sys.constant): 거절
    ---

    Returns:
        str: 거절 결과를 반환합니다.
    """
    logger.info("식당 등록 거절 요청 수신: user_id=%s", payload.user_id)
    assert payload.detail_params is not None
    double_check = payload.detail_params["double_check"].origin
    if double_check != "거절":
        logger.warning(
            "식당 등록 거절 취소: user_id=%s, double_check=%s",
            payload.user_id,
            double_check,
        )
        response = KakaoResponse()
        response.add_component(
            SimpleTextComponent(
                "등록 거절이 취소 되었습니다. 거절하시려면 다시 거절 버튼을 눌러주세요."
            )
        )
        return JSONResponse(response.get_dict())

    restaurant_id = payload.action.client_extra["identification"]
    try:
        logger.debug("식당 등록 거절 처리 시작: restaurant_id=%s", restaurant_id)
        Restaurant.decline_restaurant(restaurant_id)
    except ValueError as e:
        logger.error(
            "식당 등록 거절 실패: restaurant_id=%s, error=%s", restaurant_id, e
        )
        return JSONResponse(
            KakaoResponse().add_component(SimpleTextComponent(str(e))).get_dict()
        )
    logger.info("식당 등록 거절 완료: restaurant_id=%s", restaurant_id)
    response = KakaoResponse()
    response.add_component(SimpleTextComponent("등록이 거절되었습니다."))
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/restaurant/approve",
    openapi_extra=create_openapi_extra(
        detail_params={
            "place": {
                "origin": "교내",
                "value": "교내",
            },
        },
        client_extra={
            "identification": "test_식당_id",
        },
    ),
)
@check_access_id("sandol")
async def register_restaurant_approve(payload: Payload = Depends(parse_payload)):
    """업체 등록을 승인하는 API 입니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "업체 등록 승인"
        - 스킬: "업체 등록 승인"

    - Params:
        - detail_params:
            - place(sys.constant): 교내 또는 교외
    ---

    Returns:
        str: 승인 결과를 반환합니다.
    """
    logger.info("식당 등록 승인 요청 수신: user_id=%s", payload.user_id)
    assert payload.detail_params is not None
    location = payload.detail_params["place"].origin

    response = KakaoResponse()

    logger.debug("승인 여부 확인: location=%s", location)
    if location not in ["교내", "교외"]:
        logger.warning(
            "식당 등록 승인 취소: user_id=%s, location=%s", payload.user_id, location
        )
        response.add_component(
            SimpleTextComponent(
                "등록 승인이 취소되었습니다. 승인하시려면 다시 승인 버튼을 눌러주세요."
            )
        )
        return JSONResponse(response.get_dict())

    restaurant_id = payload.action.client_extra["identification"]

    try:
        logger.debug(
            "식당 등록 승인 처리 시작: restaurant_id=%s, location=%s",
            restaurant_id,
            location,
        )
        Restaurant.approve_restaurant(restaurant_id, location)
    except ValueError as e:
        logger.error(
            "식당 등록 승인 실패: restaurant_id=%s, error=%s", restaurant_id, e
        )
        return JSONResponse(
            KakaoResponse().add_component(SimpleTextComponent(str(e))).get_dict()
        )

    logger.info(
        "식당 등록 승인 완료: restaurant_id=%s, location=%s", restaurant_id, location
    )
    response = KakaoResponse().add_component(SimpleTextComponent("등록 완료"))
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/restaurant/list",
    openapi_extra=create_openapi_extra(utterance="식당 승인 요청 목록"),
)
@check_access_id("sandol")
async def register_restaurant_list(payload: Payload = Depends(parse_payload)):
    """등록을 신청한 업체 목록을 반환하는 API입니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화
        - "식당 승인 요청 목록"
        - "업체 승인"
        - "업체 목록"

    - OpenBuilder:
        - 블럭: "업체 목록"
        - 스킬: "업체 목록"
    ---

    Returns:
        str: 업체 목록을 반환합니다.
    """
    logger.info("등록 대기 중인 식당 목록 조회 요청 수신: user_id=%s", payload.user_id)
    data = Restaurant.load_pending_restaurants()

    response = KakaoResponse()

    if not data:
        logger.debug("등록 대기 중인 식당이 없습니다: user_id=%s", payload.user_id)
        response.add_component(SimpleTextComponent("등록 대기 중인 식당이 없습니다."))
        return JSONResponse(response.get_dict())

    logger.debug("등록 대기 중인 식당 정보 생성 시작")
    carousel = CarouselComponent()
    for apply in data:
        logger.debug("식당 정보 추가: name=%s", apply["name"])
        item_card = ItemCardComponent([])
        item_card.image_title = ImageTitle(title=apply["name"], description="식당 정보")

        opening_time = apply["opening_time"]

        item_card.add_item(
            title="점심 시간", description=Restaurant.opening_time_str(opening_time[0])
        )
        item_card.add_item(
            title="저녁 시간", description=Restaurant.opening_time_str(opening_time[1])
        )
        item_card.add_item(title="가격", description=f"{apply['price_per_person']}원")
        item_card.add_button(
            label="승인",
            action="block",
            block_id=BLOCK_IDS["approve_restaurant"],
            extra={"identification": apply["identification"]},
        )
        item_card.add_button(
            label="거절",
            action="block",
            block_id=BLOCK_IDS["decline_restaurant"],
            extra={"identification": apply["identification"]},
        )
        carousel.add_item(item_card)
    response.add_component(carousel)

    logger.info("등록 대기 중인 식당 목록 조회 완료: user_id=%s", payload.user_id)
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/restaurant",
    openapi_extra=create_openapi_extra(
        detail_params={
            "name": {
                "origin": "미가식당",
                "value": "미가식당",
            },
            "lunch_start": {
                "origin": "11:30:00",
                "value": "11:30:00",
            },
            "lunch_end": {
                "origin": "14:00:00",
                "value": "14:00:00",
            },
            "dinner_start": {
                "origin": "17:30:00",
                "value": "17:30:00",
            },
            "dinner_end": {
                "origin": "20:00:00",
                "value": "20:00:00",
            },
            "price_per_person": {
                "origin": "5000",
                "value": "5000",
            },
            "varification_key": {
                "origin": "test_식당_varification_key",
                "value": "test_식당_varification_key",
            },
            "varification_key_check": {
                "origin": "test_식당_varification_key",
                "value": "test_식당_varification_key",
            },
        },
    ),
)
async def register_restaurant(payload: Payload = Depends(parse_payload)):
    """업체 등록 신청을 관리하는 API입니다.

    등록하려는 업체의 등록 정보를 받아 신청 리스트에 저장합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화
        - "업체 등록"
        - "식당 등록"

    - OpenBuilder:
        - 블럭: "업체 등록"
        - 스킬: "업체 등록"

    - Params:
        - detail_params:
            - name(sys.constant): 업체 이름
            - lunch_start(sys.plugin.time): 점심 시작 시간
            - lunch_end(sys.plugin.time): 점심 종료 시간
            - dinner_start(sys.plugin.time): 저녁 시작 시간
            - dinner_end(sys.plugin.time): 저녁 종료 시간
            - price_per_person(sys.constant): 인당 가격
            - varification_key(sys.constant): 인증키
            - varification_key_check(sys.constant): 인증키 확인
    ---

    Returns:
        str: 업체 등록 결과를 반환합니다.
    """
    logger.info("식당 등록 요청 수신: user_id=%s", payload.user_id)
    assert payload.detail_params is not None

    logger.debug("인증키 확인: user_id=%s", payload.user_id)
    if (
        payload.detail_params["varification_key"].origin
        != payload.detail_params["varification_key_check"].origin
    ):
        logger.warning("인증키 불일치: user_id=%s", payload.user_id)
        return JSONResponse(
            KakaoResponse()
            .add_component(SimpleTextComponent("인증키가 일치하지 않습니다."))
            .get_dict()
        )

    logger.debug("식당 정보 저장: user_id=%s", payload.user_id)
    lunch_start_hours, lunch_start_minutes, _ = map(
        int, payload.action.detail_params["lunch_start"].origin.split(":")
    )
    lunch_end_hours, lunch_end_minutes, _ = map(
        int, payload.action.detail_params["lunch_end"].origin.split(":")
    )
    dinner_start_hours, dinner_start_minutes, _ = map(
        int, payload.action.detail_params["dinner_start"].origin.split(":")
    )
    dinner_end_hours, dinner_end_minutes, _ = map(
        int, payload.action.detail_params["dinner_end"].origin.split(":")
    )

    opening_time = [
        [
            (lunch_start_hours, lunch_start_minutes),
            (lunch_end_hours, lunch_end_minutes),
        ],
        [
            (dinner_start_hours, dinner_start_minutes),
            (dinner_end_hours, dinner_end_minutes),
        ],
    ]

    temp_data = {
        "identification": payload.user_id,
        "name": payload.action.detail_params["name"].origin,
        "price_per_person": int(
            payload.action.detail_params["price_per_person"].origin
        ),
        "opening_time": opening_time,
        "varification_key": payload.action.detail_params["varification_key"].origin,
    }
    logger.debug("식당 정보: %s", temp_data)

    logger.debug("식당 등록 신청 처리 시작: user_id=%s", payload.user_id)
    try:
        Restaurant.register_new_restaurant(temp_data)
    except ValueError as e:
        logger.error("식당 등록 신청 실패: user_id=%s, error=%s", payload.user_id, e)
        return JSONResponse(
            KakaoResponse().add_component(SimpleTextComponent(str(e))).get_dict()
        )

    response = KakaoResponse()
    response.add_component(
        SimpleTextComponent("아래 정보로 식당 등록 신청이 완료되었습니다.")
    )

    item_card = ItemCardComponent([])
    item_card.image_title = ImageTitle(title=temp_data["name"], description="식당 정보")
    item_card.add_item(
        title="점심 시간", description=Restaurant.opening_time_str(opening_time[0])
    )
    item_card.add_item(
        title="저녁 시간", description=Restaurant.opening_time_str(opening_time[1])
    )
    item_card.add_item(title="가격", description=f"{temp_data['price_per_person']}원")
    response.add_component(item_card)

    logger.info(
        "식당 등록 완료: user_id=%s, restaurant_name=%s",
        payload.user_id,
        temp_data["name"],
    )

    return JSONResponse(response.get_dict())


@meal_api.post("/register/delete/{meal_type}", openapi_extra=create_openapi_extra())
@check_access_id("restaurant")
async def meal_delete(meal_type: str, payload: Payload = Depends(parse_payload)):
    """삭제할 메뉴를 선택하는 API입니다.

    meal_type에 해당하는 식사 종류의 메뉴를 삭제할 수 있도록
    각 메뉴를 퀵리플라이로 반환합니다.
    퀵리플라이를 통해 삭제할 메뉴를 선택하면 meal_menu_delete API로 이동합니다.
    삭제할 메뉴가 없을 경우 "삭제할 메뉴가 없습니다."를 반환합니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작 방식: 버튼 연결

    - OpenBuilder:
        - 블럭:
            - "메뉴 삭제 - 중식"
            - "메뉴 삭제 - 석식"
        - 스킬:
            - "중식 삭제"
            - "석식 삭제"
    ---

    Returns:
        str: 삭제할 수 있는 메뉴 리스트를 반환합니다.
    """
    logger.info(
        "메뉴 삭제 요청 수신: user_id=%s, meal_type=%s", payload.user_id, meal_type
    )
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    # meal_type에 해당하는 메뉴 리스트를 불러와 퀵리플라이로 반환
    memu_list = getattr(restaurant, f"temp_{meal_type}")
    if not memu_list:
        logger.warning(
            "삭제할 메뉴가 없음: user_id=%s, meal_type=%s", payload.user_id, meal_type
        )
        return JSONResponse(
            KakaoResponse()
            .add_component(SimpleTextComponent("삭제할 메뉴가 없습니다."))
            .get_dict()
        )
    response = KakaoResponse()
    simple_text = SimpleTextComponent("삭제할 메뉴를 선택해주세요.")
    response = response.add_component(simple_text)
    logger.debug(
        "삭제 가능한 메뉴 리스트 생성: user_id=%s, meal_type=%s, menu_list=%s",
        payload.user_id,
        meal_type,
        memu_list,
    )
    for menu in memu_list:
        quick_reply = QuickReply(
            label=menu,
            action=ActionEnum.BLOCK,
            block_id=BLOCK_IDS["delete_menu"],
            extra={"meal_type": meal_type, "menu": menu},
        )
        response += quick_reply
    logger.info(
        "메뉴 삭제 리스트 반환 완료: user_id=%s, meal_type=%s",
        payload.user_id,
        meal_type,
    )
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/delete_all",
    openapi_extra=create_openapi_extra(utterance="식단 전체 삭제"),
)
@check_access_id("restaurant")
async def meal_delete_all(payload: Payload = Depends(parse_payload)):
    """모든 메뉴를 삭제하는 API입니다.

    모든 메뉴를 삭제하고 삭제된 결과를 응답으로 반환합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "식단 삭제"
        - 스킬: "식단 삭제"
    ---

    Returns:
        str: 모든 메뉴가 삭제되었음을 반환합니다.
    """
    logger.info("모든 메뉴 삭제 요청 수신: user_id=%s", payload.user_id)
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()
    logger.debug("메뉴 삭제 시작: user_id=%s", payload.user_id)
    restaurant.clear_menu()
    restaurant.save_temp_menu()
    logger.info("모든 메뉴 삭제 완료: user_id=%s", payload.user_id)
    response = KakaoResponse().add_component(
        SimpleTextComponent("모든 메뉴가 삭제되었습니다.")
    )
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/delete_menu",
    openapi_extra=create_openapi_extra(
        client_extra={
            "meal_type": "lunch",
            "menu": "김치찌개",
        },
    ),
)
@check_access_id("restaurant")
async def meal_menu_delete(payload: Payload = Depends(parse_payload)):
    """선택한 메뉴를 삭제하는 API입니다.

    meal_delete API에서 선택한 메뉴를 삭제합니다.
    삭제된 결과를 응답으로 반환합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "메뉴 삭제"
        - 스킬: "메뉴 삭제"

    - Params:
        - client_extra:
            - meal_type(str): 삭제할 식사 종류
            - menu(str): 삭제할 메뉴
    ---

    Returns:
        str: 메뉴가 삭제된 결과를 반환합니다.
    """
    logger.info("메뉴 삭제 요청 수신: user_id=%s", payload.user_id)
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    meal_type = payload.action.client_extra["meal_type"]
    menu = payload.action.client_extra["menu"]

    try:
        logger.debug(
            "메뉴 삭제 시도: user_id=%s, meal_type=%s, menu=%s",
            payload.user_id,
            meal_type,
            menu,
        )
        restaurant.delete_menu(meal_type, menu)
    except ValueError as e:
        if str(e) == "해당 메뉴는 등록되지 않은 메뉴입니다.":
            logger.warning(
                "메뉴 삭제 실패(등록되지 않음): user_id=%s, meal_type=%s, menu=%s",
                payload.user_id,
                meal_type,
                menu,
            )
            return JSONResponse(
                meal_error_response_maker("등록되지 않은 메뉴입니다.").get_dict()
            )
        else:
            logger.error(
                "메뉴 삭제 실패(예외 발생): user_id=%s, meal_type=%s, menu=%s, error=%s",
                payload.user_id,
                meal_type,
                menu,
                e,
            )
            raise e

    restaurant.save_temp_menu()

    lunch, dinner = make_meal_cards([restaurant], is_temp=True)
    response = meal_response_maker(lunch, dinner)

    logger.info(
        "메뉴 삭제 완료: user_id=%s, meal_type=%s, menu=%s",
        payload.user_id,
        meal_type,
        menu,
    )
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/register/{meal_type}",
    openapi_extra=create_openapi_extra(
        detail_params={
            "menu": {
                "origin": "김치찌개",
                "value": "김치찌개",
            },
        },
    ),
)
@check_access_id("restaurant")
async def meal_register(meal_type: str, payload: Payload = Depends(parse_payload)):
    """식단 정보를 등록합니다.

    중식 등록 및 석식 등록 스킬을 처리합니다.
    중식 및 석식 등록 발화시 호출되는 API입니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작 방식: 발화
        - "중식 등록"
        - "석식 등록"

    - OpenBuilder:
        - 블럭:
            - "식단 등록 - 중식"
            - "식단 등록 - 석식"
        - 스킬:
            - "중식 등록"
            - "석식 등록"
    ---

    - Params:
        - detail_params:
            - menu(sys.plugin.text): 등록할 메뉴
    """
    logger.info(
        "식단 등록 요청 수신: user_id=%s, meal_type=%s", payload.user_id, meal_type
    )
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    assert payload.detail_params is not None
    menu_list = split_string(payload.detail_params["menu"].origin)

    logger.debug(
        "식단 등록 메뉴 리스트 생성: user_id=%s, meal_type=%s, menu_list=%s",
        payload.user_id,
        meal_type,
        menu_list,
    )
    for menu in menu_list:
        try:
            restaurant.add_menu(meal_type, menu)
        except ValueError as e:
            if str(e) != "해당 메뉴는 이미 메뉴 목록에 존재합니다.":
                logger.error(
                    "식단 등록 실패: user_id=%s, meal_type=%s, menu=%s, error=%s",
                    payload.user_id,
                    meal_type,
                    menu,
                    e,
                )
                raise e

    restaurant.save_temp_menu()

    lunch, dinner = make_meal_cards([restaurant], is_temp=True)
    response = meal_response_maker(lunch, dinner)

    logger.info("식단 등록 완료: user_id=%s, meal_type=%s", payload.user_id, meal_type)
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/submit",
    openapi_extra=create_openapi_extra()
)
@check_tip_and_e
@check_access_id("restaurant")
async def meal_submit(payload: Payload = Depends(parse_payload)):
    """식단 정보를 확정하는 API입니다.

    임시 저장된 식단 정보를 확정하고 등록합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "식단 확정"
        - 스킬: "식단 확정"
    ---

    Returns:
        str: 확정된 식단 정보를 반환합니다.
    """
    # 요청을 받아 Payload 객체로 변환 및 사용자의 ID로 등록된 식당 객체를 불러옴
    logger.info("식단 확정 요청 수신: user_id=%s", payload.user_id)
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    logger.debug("식단 확정 처리 시작: user_id=%s", payload.user_id)
    # 식당 정보를 확정 등록
    try:
        restaurant.submit()
    except ValueError as e:
        if (
            str(e)
            == f"레스토랑 '{restaurant.name}'가 test.json 파일에 존재하지 않습니다."
        ):
            logger.error(
                "식단 확정 실패(저장된 정보 없음): user_id=%s, restaurant_name=%s",
                payload.user_id,
                restaurant.name,
            )
            return JSONResponse(
                KakaoResponse()
                .add_component(
                    SimpleTextComponent(
                        "저장된 식당 정보가 없습니다. 관리자에게 문의해주세요."
                    )
                )
                .get_dict()
            )
        else:
            logger.error(
                "식단 확정 실패(예외 발생): user_id=%s, restaurant_name=%s, error=%s",
                payload.user_id,
                restaurant.name,
                e,
            )
            raise e

    # 확정된 식당 정보를 다시 불러와 카드를 생성
    saved_restaurant: Restaurant = Restaurant.by_id(payload.user_id)
    lunch, dinner = make_meal_cards([saved_restaurant])

    # 응답 생성
    response = KakaoResponse()
    submit_message = SimpleTextComponent(
        "식단 정보가 아래 내용으로 확정 등록되었습니다."
    )
    response.add_component(submit_message)
    response.add_component(lunch)
    response.add_component(dinner)

    logger.info(
        "식단 확정 완료: user_id=%s, restaurant_name=%s",
        payload.user_id,
        saved_restaurant.name,
    )
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/view",
    openapi_extra=create_openapi_extra(
        detail_params={
            "Cafeteria": {
                "origin": "미가",
                "value": "미가식당",
            },
        },
        utterance="학식 미가",
    ),
)
@check_tip_and_e
async def meal_view(payload: Payload = Depends(parse_payload)):
    """식단 정보를 Carousel TextCard 형태로 반환합니다.

    등록된 식당 정보를 불러와 어제 7시 이후 등록된 식당 정보를 먼저 배치합니다.
    그 후 어제 7시 이전 등록된 식당 정보를 배치합니다.
    이를 통해 어제 7시 이후 등록된 식당 정보가 먼저 보이도록 합니다.
    이를 토대로 점심과 저녁 메뉴를 담은 Carousel을 생성합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 발화
        - "학식"
        - "학식 <식당>"
        - "메뉴 <식당>"
        - 등

    - OpenBuilder:
        - 블럭: "학식 보기"
        - 스킬: "학식 보기"

    - Params:
        - detail_params:
            - Cafeteria(식당): 식당 이름(Optional)
    ---

    Returns:
        str: 식단 정보를 반환합니다.
    """
    logger.info("식단 정보 조회 요청 수신: user_id=%s", payload.user_request.user.id)
    # payload에서 Cafeteria 값 추출
    assert payload.action.detail_params is not None
    cafeteria = payload.action.detail_params.get("Cafeteria")  # 학식 이름
    target_cafeteria = getattr(cafeteria, "value", None)

    # 식당 정보를 가져옵니다.
    cafeteria_list: list[Restaurant] = await get_meals()

    # cafeteria 값이 있을 경우 해당 식당 정보로 필터링
    if target_cafeteria:
        logger.debug("식단 정보 필터링: target_cafeteria=%s", target_cafeteria)
        restaurants = list(filter(lambda x: x.name == target_cafeteria, cafeteria_list))
    else:
        restaurants = cafeteria_list

    # 어제 7시를 기준으로 식당 정보를 필터링
    standard_time = datetime.now(tz=KST) - timedelta(days=1)
    standard_time = standard_time.replace(hour=19, minute=0, second=0, microsecond=0)

    af_standard: list[Restaurant] = []
    bf_standard: list[Restaurant] = []
    logger.debug("식당 정보 정렬 시작: user_id=%s", payload.user_request.user.id)
    for r in restaurants:
        if r.registration_time.tzinfo is None:
            logger.warning(
                "등록시간에 시간대 정보가 없어 9시간을 더해 KST로 변환합니다."
            )
            temp = r.registration_time + timedelta(hours=9)
            r.registration_time = temp.replace(tzinfo=KST)
        if r.registration_time < standard_time:
            logger.debug("식당 정보 정렬: %s | 어제 7시 이전 등록", r.name)
            bf_standard.append(r)
        else:
            logger.debug("식당 정보 정렬: %s | 어제 7시 이후 등록", r.name)
            af_standard.append(r)

    bf_standard.sort(key=lambda x: x.registration_time)
    af_standard.sort(key=lambda x: x.registration_time)

    # 어제 7시 이후 등록된 식당 정보를 먼저 배치
    restaurants = af_standard + bf_standard

    # 점심과 저녁 메뉴를 담은 Carousel 생성
    lunch_carousel, dinner_carousel = make_meal_cards(restaurants)

    response = KakaoResponse()

    # 점심과 저녁 메뉴 Carousel을 SkillList에 추가
    # 비어있는 Carousel을 추가하지 않음
    if not lunch_carousel.is_empty:
        response.add_component(lunch_carousel)
    if not dinner_carousel.is_empty:
        response.add_component(dinner_carousel)
    if not response.component_list:
        logger.debug("식단 정보가 없습니다: user_id=%s", payload.user_request.user.id)
        response.add_component(SimpleTextComponent("식단 정보가 없습니다."))

    # 퀵리플라이 추가
    # 현재 선택된 식단을 제외한 다른 식당을 퀵리플라이로 추가
    if target_cafeteria:
        response.add_quick_reply(
            label="모두 보기",
            action="message",
            message_text="학식",
        )

    for rest in cafeteria_list:
        if rest.name != target_cafeteria:
            response.add_quick_reply(
                label=rest.name,
                action="message",
                message_text=f"학식 {rest.name}",
            )

    logger.info("식단 정보 조회 완료: user_id=%s", payload.user_request.user.id)
    return JSONResponse(response.get_dict())


@meal_api.post(
    "/restaurant",
    openapi_extra=create_openapi_extra(
        client_extra={
            "restaurant_name": "미가식당",
        }
    ),
)
async def meal_restaurant(payload: pydanticPayload = Depends(parse_payload)):
    """식당 정보를 반환하는 API입니다.

    식당의 운영시간, 위치, 가격 등의 정보를 반환합니다.

    ## 카카오 챗봇 연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        블럭: "식당 정보"
        스킬: "식당 정보"

    - Params:
        - client_extra:
            - restaurant_name(str): 식당 이름
    ---

    Returns:
        str: 식당 정보를 반환합니다.
    """
    logger.info("식당 정보 조회 요청 수신: user_id=%s", payload.user_id)
    restaurant_name: str = payload.action.client_extra["restaurant_name"]

    # 식당 정보를 가져옵니다.
    cafeteria_list: list[Restaurant] = await get_meals()

    restaurant: Restaurant = list(
        filter(lambda x: x.name == restaurant_name, cafeteria_list)
    )[0]

    item_card = ItemCardComponent([])
    item_card.image_title = ImageTitle(title=restaurant.name, description="식당 정보")
    item_card.add_item(title="점심 시간", description=restaurant.lunch_time)
    item_card.add_item(title="저녁 시간", description=restaurant.dinner_time)
    item_card.add_item(title="위치", description=restaurant.location)
    item_card.add_item(title="가격", description=f"{restaurant.price_per_person}원")
    item_card.add_button(
        label="메뉴 보기", action="message", message_text=f"학식 {restaurant_name}"
    )
    url = NAVER_MAP_URL_DICT.get(restaurant_name, None)
    if url:
        item_card.add_button(
            label="식당 위치 지도 보기", action="webLink", web_link_url=url
        )
    response = KakaoResponse().add_component(item_card)

    logger.info(
        "식당 정보 조회 완료: user_id=%s, restaurant_name=%s",
        payload.user_id,
        restaurant_name,
    )

    return JSONResponse(response.get_dict())


@meal_api.post("/validation/menu")
async def validation_menu(request: Request):
    """메뉴 유효성 검사 API입니다."""
    payload = ValidationPayload.from_dict(await request.json())

    menu_list = split_string(payload.utterance)

    if len(menu_list) > 5:
        response = ValidationResponse(
            status="ERROR",
            message="메뉴는 5개까지만 등록할 수 있습니다.\n다시 입력해주세요.",
        )
    else:
        response = ValidationResponse(status="SUCCESS")
    return JSONResponse(response.get_dict())
