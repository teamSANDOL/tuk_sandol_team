"""학식 관련 API 파일

학식 관련 API가 작성되어 있습니다.
학식 보기, 등록, 삭제 등의 기능을 담당합니다.
"""

from datetime import datetime, timedelta

from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from kakao_chatbot import Payload, ValidationPayload
from kakao_chatbot.response import (
    KakaoResponse, QuickReply, ActionEnum, ValidationResponse
)
from kakao_chatbot.response.components import CarouselComponent, SimpleTextComponent, ItemCardComponent, ImageTitle

from api_server.utils import (
    meal_error_response_maker, split_string,
    meal_response_maker, make_meal_cards,
    parse_payload, check_tip_and_e,
)
from api_server.settings import NAVER_MAP_URL_DICT, logger
from crawler import (
    get_registration, Restaurant, get_meals
)
from crawler.settings import KST, _PATH

import json

meal_api = APIRouter(prefix="/meal")

@meal_api.post("/register/restaurant/decline")
async def register_restaurant_decline(payload: Payload = Depends(parse_payload)):
    assert payload.detail_params is not None
    double_check = payload.detail_params["double_check"].origin
    if double_check not in ['예', '네', 'ㅖ', '응', '어']:
        response = KakaoResponse()
        response.add_component(
            SimpleTextComponent(
                "등록 거절이 취소 되었습니다. 거절하시려면 다시 거절 버튼을 눌러주세요."
            )
        ).get_dict()
        return JSONResponse(response.get_dict())
    
    restaurant_id = payload.action.client_extra["identification"]
    with open(f"{_PATH}/data/restaurant_register.json", "r") as f:
        data = json.load(f)
    
    restaurant_data = list(filter(lambda x: x["identification"] != restaurant_id, data))
    
    with open(f"{_PATH}/data/restaurant_register.json", "w") as f:
        json.dump(restaurant_data, f, indent=4)
    response = KakaoResponse()
    response.add_component(
        SimpleTextComponent("등록이 거절되었습니다.")
    )
    return JSONResponse(response.get_dict())

@meal_api.post("/register/restaurant/approve")
async def register_restaurant_approve(payload: Payload = Depends(parse_payload)):
    assert payload.detail_params is not None
    location = payload.detail_params["place"].origin

    response = KakaoResponse()
    if location not in ["교내", "교외"]:
        response.add_component(
            SimpleTextComponent(
                "등록 승인이 취소되었습니다. 승인하시려면 다시 승인 버튼을 눌러주세요."
            )
        ).get_dict()
        return JSONResponse(response.get_dict())

    restaurant_id = payload.action.client_extra["identification"]
    with open(f"{_PATH}/data/restaurant_register.json", "r") as f:
        data = json.load(f)
    
    restaurant_data_list = list(filter(lambda x: x["identification"] == restaurant_id, data))
    restaurant_data = restaurant_data_list[0]
    identification = restaurant_data["identification"]
    name = restaurant_data["name"]
    price_per_person = restaurant_data["price_per_person"]
    opening_time = restaurant_data["opening_time"]

    Restaurant.init_restaurant(
        identification, name, opening_time, location, price_per_person
    )

    new_restaurant_data = list(filter(lambda x: x["identification"] != restaurant_id, data))
    
    with open(f"{_PATH}/data/restaurant_register.json", "w") as f:
        json.dump(new_restaurant_data, f, indent=4)

    response = KakaoResponse().add_component(
        SimpleTextComponent("등록 완료")
    )
    
    return JSONResponse(response.get_dict())


@meal_api.post("/register/restaurant/list")
async def register_restaurant_list(payload: Payload = Depends(parse_payload)):
    """신청한 업체를 승인하는 API입니다.
    """
    with open(f"{_PATH}/data/restaurant_register.json", "r") as f:
        data = json.load(f)
    
    response = KakaoResponse()

    carousel = CarouselComponent()
    for apply in data:
        item_card = ItemCardComponent([])
        item_card.image_title = ImageTitle(
            title=apply["name"],
            description="식당 정보"
        )

        opening_time = apply["opening_time"]

        item_card.add_item(
            title="점심 시간",
            description="~".join(opening_time[0])
        )
        item_card.add_item(
            title="저녁 시간",
            description="~".join(opening_time[1])
        )
        item_card.add_item(
            title="가격",
            description=f"{apply['price_per_person']}원"
        )
        item_card.add_button(
            label="승인",
            action="block",
            block_id="673ab011bdae5e01db2d959d",
            extra={"identification": apply["identification"]}
        )
        item_card.add_button(
            label="거절",
            action="block",
            block_id="673ab1fb72ca387abe6381b7",
            extra={"identification": apply["identification"]}
        )
        carousel.add_item(item_card)
    response.add_component(carousel)

    return JSONResponse(response.get_dict())





@meal_api.post("/register/restaurant")
async def register_restaurant(payload: Payload = Depends(parse_payload)):
    """업체 등록 신청을 관리하는 API입니다.
    """
    lunch_start_hours, lunch_start_minutes, _ = map(
        int, payload.action.detail_params["lunch_start"].origin.split(':'))
    lunch_end_hours, lunch_end_minutes, _ = map(
        int, payload.action.detail_params["lunch_end"].origin.split(':'))
    dinner_start_hours, dinner_start_minutes, _ = map(
        int, payload.action.detail_params["dinner_start"].origin.split(':'))
    dinner_end_hours, dinner_end_minutes, _ = map(
        int, payload.action.detail_params["dinner_end"].origin.split(':'))

    if lunch_start_hours > 12:
        lunch_start_hours -= 12
        lunch_start_hours = f"오후 {str(lunch_start_hours).zfill(2)}"
    else:
        lunch_start_hours = f"오전 {str(lunch_start_hours).zfill(2)}"

    if lunch_end_hours > 12:
        lunch_end_hours -= 12
    lunch_end_hours = str(lunch_end_hours).zfill(2)
    

    if dinner_start_hours > 12:
        dinner_start_hours -= 12
        dinner_start_hours = f"오후 {str(dinner_start_hours).zfill(2)}"
    else:
        dinner_start_hours = f"오전 {str(dinner_start_hours).zfill(2)}"
    
    if dinner_end_hours > 12:
        dinner_end_hours -= 12
    dinner_end_hours = str(dinner_end_hours).zfill(2)

    lunch_time = [f"{lunch_start_hours}:{lunch_start_minutes}",
                  f"{lunch_end_hours}:{lunch_end_minutes}"]
    dinner_time = [f"{dinner_start_hours}:{dinner_start_minutes}",
                   f"{dinner_end_hours}:{dinner_end_minutes}"]

    opening_time = [lunch_time, dinner_time]

    temp_data = {
        "identification": payload.user_id,
        "name": payload.action.detail_params["name"].origin,
        "price_per_person": int(payload.action.detail_params["price_per_person"].origin),
        "opening_time": opening_time,
    }

    try:
        with open(f"{_PATH}/data/restaurant_register.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(temp_data)

    with open(f"{_PATH}/data/restaurant_register.json", "w") as f:
        json.dump(data, f, indent=4)

    response = KakaoResponse()
    response.add_component(
        SimpleTextComponent("아래 정보로 식당 등록 신청이 완료되었습니다.")
    )

    item_card = ItemCardComponent([])
    item_card.image_title = ImageTitle(
        title=temp_data["name"],
        description="식당 정보"
    )
    item_card.add_item(
        title="점심 시간",
        description="~".join(opening_time[0])
    )
    item_card.add_item(
        title="저녁 시간",
        description="~".join(opening_time[1])
    )
    item_card.add_item(
        title="가격",
        description=f"{temp_data['price_per_person']}원"
    )
    response.add_component(item_card)

    return JSONResponse(response.get_dict())


@meal_api.post("/register/delete/{meal_type}")
async def meal_delete(meal_type: str, payload: Payload = Depends(parse_payload)):
    """삭제할 메뉴를 선택하는 API입니다.

    meal_type에 해당하는 식사 종류의 메뉴를 삭제할 수 있도록
    각 메뉴를 퀵리플라이로 반환합니다.
    퀵리플라이를 통해 삭제할 메뉴를 선택하면 meal_menu_delete API로 이동합니다.
    삭제할 메뉴가 없을 경우 "삭제할 메뉴가 없습니다."를 반환합니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.
    """
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    # meal_type에 해당하는 메뉴 리스트를 불러와 퀵리플라이로 반환
    memu_list = getattr(restaurant, f"temp_{meal_type}")
    if not memu_list:
        return JSONResponse(
            KakaoResponse().add_component(
                SimpleTextComponent("삭제할 메뉴가 없습니다.")
            ).get_dict()
        )
    response = KakaoResponse()
    simple_text = SimpleTextComponent("삭제할 메뉴를 선택해주세요.")
    response = response.add_component(simple_text)
    for menu in memu_list:
        quick_reply = QuickReply(
            label=menu,
            action=ActionEnum.BLOCK,
            block_id="67218366770f3e5a431708ac",
            extra={"meal_type": meal_type, "menu": menu},
        )
        response += quick_reply
    return JSONResponse(response.get_dict())


@meal_api.post("/register/delete_all")
async def meal_delete_all(payload: Payload = Depends(parse_payload)):
    """모든 메뉴를 삭제하는 API입니다.

    모든 메뉴를 삭제하고 삭제된 결과를 응답으로 반환합니다.
    """
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()
    restaurant.clear_menu()
    restaurant.save_temp_menu()
    response = KakaoResponse().add_component(
        SimpleTextComponent("모든 메뉴가 삭제되었습니다.")
    )
    return JSONResponse(response.get_dict())


@meal_api.post("/register/delete_menu")
async def meal_menu_delete(payload: Payload = Depends(parse_payload)):
    """선택한 메뉴를 삭제하는 API입니다.

    meal_delete API에서 선택한 메뉴를 삭제합니다.
    삭제된 결과를 응답으로 반환합니다.
    """
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    meal_type = payload.action.client_extra["meal_type"]
    menu = payload.action.client_extra["menu"]

    try:
        restaurant.delete_menu(meal_type, menu)
    except ValueError as e:
        if str(e) == "해당 메뉴는 등록되지 않은 메뉴입니다.":
            return JSONResponse(
                meal_error_response_maker("등록되지 않은 메뉴입니다.").get_dict()
            )
        else:
            raise e

    restaurant.save_temp_menu()

    lunch, dinner = make_meal_cards([restaurant], is_temp=True)
    response = meal_response_maker(lunch, dinner)

    return JSONResponse(response.get_dict())


@meal_api.post("/register/{meal_type}")
async def meal_register(meal_type: str, payload: Payload = Depends(parse_payload)):
    """식단 정보를 등록합니다.

    중식 등록 및 석식 등록 스킬을 처리합니다.
    중식 및 석식 등록 발화시 호출되는 API입니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.
    """

    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    # 카카오에서 전달받은 menu 파라미터를 구분자를 기준으로 분리해 리스트로 변환
    assert payload.detail_params is not None
    menu_list = split_string(
        payload.detail_params["menu"].origin)

    # TODO(Seokyoung_Hong): 메뉴 등록 개수 제한기능 필요시 활성화
    # if len(getattr(restaurant, f"temp_{meal_type}", []) + menu_list) > 5:
    #     return meal_error_response_maker("메뉴는 5개까지만 등록할 수 있습니다.").get_json()

    # 메뉴를 등록
    for menu in menu_list:
        try:
            restaurant.add_menu(meal_type, menu)
        except ValueError as e:
            if str(e) != "해당 메뉴는 이미 메뉴 목록에 존재합니다.":
                raise e

    restaurant.save_temp_menu()

    lunch, dinner = make_meal_cards([restaurant], is_temp=True)
    response = meal_response_maker(lunch, dinner)

    return JSONResponse(response.get_dict())


@meal_api.post("/submit")
@check_tip_and_e
async def meal_submit(payload: Payload = Depends(parse_payload)):
    """식단 정보를 확정하는 API입니다.

    임시 저장된 식단 정보를 확정하고 등록합니다.
    """
    # 요청을 받아 Payload 객체로 변환 및 사용자의 ID로 등록된 식당 객체를 불러옴
    restaurant: Restaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    logger.info("확정 시작")
    # 식당 정보를 확정 등록
    try:
        restaurant.submit()
    except ValueError as e:
        if str(e) == f"레스토랑 '{restaurant.name}'가 test.json 파일에 존재하지 않습니다.":
            return JSONResponse(
                KakaoResponse().add_component(
                    SimpleTextComponent("저장된 식당 정보가 없습니다. 관리자에게 문의해주세요.")
                ).get_dict()
            )
        else:
            raise e
    # finally:
    #     del restaurant

    logger.info("확정 작업 완료 | 확정 정보 불러오기")

    # 확정된 식당 정보를 다시 불러와 카드를 생성
    saved_restaurant: Restaurant = Restaurant.by_id(
        payload.user_id)
    lunch, dinner = make_meal_cards([saved_restaurant])

    # 응답 생성
    response = KakaoResponse()
    submit_message = SimpleTextComponent("식단 정보가 아래 내용으로 확정 등록되었습니다.")
    response.add_component(submit_message)
    response.add_component(lunch)
    response.add_component(dinner)

    logger.info("확정 정보 반환")
    return JSONResponse(response.get_dict())


@meal_api.post("/view")
@check_tip_and_e
async def meal_view(payload: Payload = Depends(parse_payload)):
    """식단 정보를 Carousel TextCard 형태로 반환합니다."""
    # payload에서 Cafeteria 값 추출
    assert payload.detail_params is not None
    cafeteria = payload.detail_params.get("Cafeteria")  # 학식 이름
    target_cafeteria = getattr(cafeteria, "value", None)

    # 식당 정보를 가져옵니다.
    cafeteria_list: list[Restaurant] = await get_meals()

    # cafeteria 값이 있을 경우 해당 식당 정보로 필터링
    if target_cafeteria:
        restaurants = list(
            filter(lambda x: x.name == target_cafeteria, cafeteria_list))
    else:
        restaurants = cafeteria_list

    # 어제 7시를 기준으로 식당 정보를 필터링
    standard_time = datetime.now(tz=KST) - timedelta(days=1)
    standard_time = standard_time.replace(
        hour=19, minute=0, second=0, microsecond=0)

    af_standard: list[Restaurant] = []
    bf_standard: list[Restaurant] = []
    for r in restaurants:
        if r.registration_time.tzinfo is None:
            logger.warning("등록시간에 시간대 정보가 없어 9시간을 더해 KST로 변환합니다.")
            temp = r.registration_time + timedelta(hours=9)
            r.registration_time = temp.replace(tzinfo=KST)
        if r.registration_time < standard_time:
            bf_standard.append(r)
        else:
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
        response.add_component(
            SimpleTextComponent("식단 정보가 없습니다.")
        )

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

    return JSONResponse(response.get_dict())


@meal_api.post("/restaurant")
async def meal_restaurant(payload: Payload = Depends(parse_payload)):
    """식당 정보를 반환하는 API입니다."""
    restaurant_name: str = payload.action.client_extra["restaurant_name"]

    # 식당 정보를 가져옵니다.
    cafeteria_list: list[Restaurant] = await get_meals()

    restaurant: Restaurant = list(
        filter(lambda x: x.name == restaurant_name, cafeteria_list))[0]

    item_card = ItemCardComponent([])
    item_card.image_title = ImageTitle(
        title=restaurant.name,
        description="식당 정보"
    )
    item_card.add_item(
        title="점심 시간",
        description="~".join(restaurant.opening_time[0])
    )
    item_card.add_item(
        title="저녁 시간",
        description="~".join(restaurant.opening_time[1])
    )
    item_card.add_item(
        title="위치",
        description=restaurant.location
    )
    item_card.add_item(
        title="가격",
        description=f"{restaurant.price_per_person}원"
    )
    item_card.add_button(
        label="메뉴 보기",
        action="message",
        message_text=f"학식 {restaurant_name}"
    )
    url = NAVER_MAP_URL_DICT.get(restaurant_name, None)
    if url:
        item_card.add_button(
            label="식당 위치 지도 보기",
            action="webLink",
            web_link_url=url
        )
    response = KakaoResponse().add_component(item_card)

    return JSONResponse(response.get_dict())


@meal_api.post("/validation/menu")
async def validation_menu(request: Request):
    """메뉴 유효성 검사 API입니다."""
    payload = ValidationPayload.from_dict(await request.json())

    menu_list = split_string(
        payload.utterance)

    if len(menu_list) > 5:
        response = ValidationResponse(
            status="ERROR", message="메뉴는 5개까지만 등록할 수 있습니다.\n다시 입력해주세요.")
    else:
        response = ValidationResponse(status="SUCCESS")
    return JSONResponse(response.get_dict())
