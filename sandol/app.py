"""Sandol의 메인 애플리케이션 파일입니다."""
from flask import Flask, request

from .api_server.utils import (
    meal_response_maker, make_meal_cards, split_string, handle_errors,
    error_message)
from .crawler import get_registration, RegistrationRestaurant, Restaurant, get_meals

from .api_server.kakao import Payload
from .api_server.kakao.response import KakaoResponse, QuickReply, ActionEnum
from .api_server.kakao.response.components import SimpleTextComponent, TextCardComponent

app = Flask(__name__)


@app.route("/")
def root():
    """루트 페이지입니다."""
    return "Hello Sandol"


@app.route("/meal/register/<meal_type>", methods=["POST"])
@handle_errors
def meal_register(meal_type: str):
    """식단 정보를 등록합니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.

    중식 등록 및 석식 등록 스킬을 처리합니다.
    중식 및 석식 등록 발화시 호출되는 API입니다.
    """

    # 요청을 받아 Payload 객체로 변환
    payload = Payload.from_dict(request.json)  # type: ignore

    # 사용자의 ID로 등록된 식당 객체를 불러옴
    restaurant: RegistrationRestaurant = get_registration(
        payload.user_id)
    restaurant.load_temp_menu()

    # 카카오에서 전달받은 menu 파라미터를 구분자를 기준으로 분리해 리스트로 변환
    menu_list = split_string(
        payload.detail_params["menu"].origin)  # type: ignore

    # 메뉴를 등록
    for menu in menu_list:
        try:
            restaurant.add_menu(meal_type, menu)

        # ValueError중 메뉴가 이미 존재하는 경우만 무시
        # 그 외의 모든 에러는 에러 정보와 함께 에러 메시지를 반환
        except ValueError as e:
            if str(e) != "해당 메뉴는 이미 메뉴 목록에 존재합니다.":
                error_msg = error_message(e)
                return KakaoResponse().add_component(error_msg).get_json()

    # 임시 저장된 메뉴를 저장
    restaurant.save_temp_menu()

    # 임시 저장된 메뉴를 불러와 카드를 생성
    lunch, dinner = make_meal_cards([restaurant], is_temp=True)

    # 식단 미리보기 응답 생성
    response = meal_response_maker(lunch, dinner)

    return response.get_json()


@app.route("/meal/register/delete/<meal_type>", methods=["POST"])
@handle_errors
def meal_delete(meal_type: str):
    """삭제할 메뉴를 선택하는 API입니다.

    meal_type에 해당하는 식사 종류의 메뉴를 삭제할 수 있도록
    각 메뉴를 퀵리플라이로 반환합니다.
    퀵리플라이를 통해 삭제할 메뉴를 선택하면 meal_menu_delete API로 이동합니다.
    삭제할 메뉴가 없을 경우 "삭제할 메뉴가 없습니다."를 반환합니다.

    Args:
        meal_type (str): 중식 또는 석식을 나타내는 문자열입니다.
            lunch, dinner 2가지 중 하나의 문자열이어야 합니다.
    """
    payload = Payload.from_dict(request.json)  # type: ignore
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    memu_list = getattr(restaurant, f"temp_{meal_type}")
    if not memu_list:
        return KakaoResponse().add_component(
            SimpleTextComponent("삭제할 메뉴가 없습니다.")
        ).get_json()
    response = KakaoResponse()
    simple_text = SimpleTextComponent("삭제할 메뉴를 선택해주세요.")
    response = response.add_component(simple_text)
    for menu in memu_list:
        quick_reply = QuickReply(
            label=menu,
            action=ActionEnum.BLOCK,
            block_id="66437f48dc3e762a0216a3e0",
            extra={"meal_type": meal_type, "menu": menu},
        )
        response += quick_reply
    return response.get_json()


@app.route("/meal/register/delete_all", methods=["POST"])
@handle_errors
def meal_delete_all():
    """모든 메뉴를 삭제하는 API입니다.

    모든 메뉴를 삭제하고 삭제된 결과를 응답으로 반환합니다.
    """
    payload = Payload.from_dict(request.json)  # type: ignore
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
    restaurant.clear_menu()
    restaurant.save_temp_menu()
    response = KakaoResponse().add_component(
        SimpleTextComponent("모든 메뉴가 삭제되었습니다.")
    )
    return response.get_json()


@app.route("/meal/register/delete_menu", methods=["POST"])
@handle_errors
def meal_menu_delete():
    """선택한 메뉴를 삭제하는 API입니다.

    meal_delete API에서 선택한 메뉴를 삭제합니다.
    삭제된 결과를 응답으로 반환합니다.
    """
    payload = Payload.from_dict(request.json)  # type: ignore
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    meal_type = payload.action.client_extra["meal_type"]
    menu = payload.action.client_extra["menu"]

    try:
        restaurant.delete_menu(meal_type, menu)
    except ValueError as e:
        if str(e) == "해당 메뉴는 등록되지 않은 메뉴입니다.":
            return KakaoResponse().add_component(
                SimpleTextComponent("등록되지 않은 메뉴입니다.")
            ).get_json()
        else:
            error_msg = error_message(e)
            return KakaoResponse().add_component(error_msg).get_json()
    restaurant.save_temp_menu()

    # 임시 저장된 메뉴를 불러와 카드를 생성
    lunch, dinner = make_meal_cards([restaurant], is_temp=True)

    # 식단 미리보기 응답 생성
    response = meal_response_maker(lunch, dinner)

    return response.get_json()


@app.route("/meal/submit", methods=["POST"])
@handle_errors
def meal_submit():
    """식단 정보를 확정하는 API입니다.

    임시 저장된 식단 정보를 확정하고 등록합니다.
    """

    # 요청을 받아 Payload 객체로 변환 및 사용자의 ID로 등록된 식당 객체를 불러옴
    payload = Payload.from_dict(request.json)  # type: ignore
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
    restaurant.load_temp_menu()

    # 식당 정보를 확정 등록
    try:
        restaurant.submit()

    # 에러 발생 시 에러 메시지 반환
    except ValueError as e:
        if str(e) == f"레스토랑 '{restaurant.name}'가 test.json 파일에 존재하지 않습니다.":
            return KakaoResponse().add_component(
                SimpleTextComponent("저장된 식당 정보가 없습니다. 관리자에게 문의해주세요.")
            ).get_json()
        else:
            error_msg = error_message(str(e))
            return KakaoResponse().add_component(error_msg).get_json()

    # 확정된 식당 정보를 다시 불러와 카드를 생성
    restaurant: RegistrationRestaurant = get_registration(  # type: ignore
        payload.user_id)
    lunch, dinner = make_meal_cards([restaurant])

    # 응답 생성
    response = KakaoResponse()
    submit_message = SimpleTextComponent("식단 정보가 아래 내용으로 확정 등록되었습니다.")
    response.add_component(submit_message)
    response.add_component(lunch)
    response.add_component(dinner)

    return response.get_json()


@app.route("/meal/view", methods=["POST"])
def meal_view():
    """식단 정보를 Carousel TextCard 형태로 반환합니다."""
    assert request.json is not None
    payload = Payload.from_dict(request.json)  # 요청 Payload를 파싱합니다.

    # payload에서 Cafeteria 값 추출
    cafeteria = payload.detail_params.get("Cafeteria")  # 학식 이름
    target_cafeteria = getattr(cafeteria, "value", None)

    print(f"식당: {target_cafeteria}")
    print(f"payload: {payload}")

    # 식당 정보를 가져옵니다.
    cafeteria_list: list[Restaurant] = get_meals()

    # cafeteria 값이 있을 경우 해당 식당 정보로 필터링
    if target_cafeteria:
        if target_cafeteria in ["미가", "세미콘", "수호"]:
            # 식단 정보를 해당 식당 정보로 필터링
            restaurants = [
                r for r in cafeteria_list if r.name == target_cafeteria]
        else:
            # TIP 또는 E동 식당인 경우
            return KakaoResponse().add_component(CAFETERIA_WEB).get_json()
    else:
        # cafeteria 값이 없을 경우 전체 식당 정보 반환
        restaurants = cafeteria_list

    # 점심과 저녁 메뉴를 담은 Carousel 생성
    lunch_carousel, dinner_carousel = make_meal_cards(restaurants)

    response = KakaoResponse()  # 응답 객체 생성

    # 점심과 저녁 메뉴 Carousel을 SkillList에 추가
    # 모듈에서 자동으로 비어있는 Carousel은 추가하지 않음
    response.add_component(lunch_carousel)
    response.add_component(dinner_carousel)
    if not cafeteria or cafeteria.value not in ["미가", "세미콘", "수호"]:
        response.add_component(CAFETERIA_WEB)

    # 식단 정보가 없는 경우 정보 없음 TextCard 추가
    elif response.is_empty:
        response.add_component(TextCardComponent("식단 정보가 없습니다."))

    # 도움말 추가
    response.add_quick_reply(HELP)
    response.add_quick_reply(
        label="모두 보기",
        action="message",
        message_text="테스트 학식",
    )
    for rest in cafeteria_list:
        if rest.name != target_cafeteria:
            response.add_quick_reply(
                label=rest.name,
                action="message",
                message_text=f"테스트 학식 {rest.name}",
            )




if __name__ == "__main__":
    app.run()
