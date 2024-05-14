"""Sandol의 메인 애플리케이션 파일입니다."""
from flask import Flask, request

from .api_server.utils import meal_response_maker, make_meal_cards, split_string, error_message
from .crawler import get_registration, RegistrationRestaurant

from .api_server.kakao import Payload
from .api_server.kakao.response import KakaoResponse, QuickReply, ActionEnum
from .api_server.kakao.response.components import SimpleTextComponent

app = Flask(__name__)


@app.route("/")
def root():
    """루트 페이지입니다."""
    return "Hello Sandol"


@app.post("/meal/register/<meal_type>")
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
    menu_list = split_string(payload.detail_params["menu"].origin)

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
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = error_message(e)
            return KakaoResponse().add_component(error_msg).get_json()

    # 임시 저장된 메뉴를 저장
    restaurant.save_temp_menu()

    # 임시 저장된 메뉴를 불러와 카드를 생성
    lunch, dinner = make_meal_cards([restaurant], is_temp=True)

    # 식단 미리보기 응답 생성
    response = meal_response_maker(lunch, dinner)

    return response.get_json()


@app.post("/meal/register/delete/<meal_type>")
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


@app.post("/meal/register/delete_menu")
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
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = error_message(e)
        return KakaoResponse().add_component(error_msg).get_json()
    restaurant.save_temp_menu()

    # 임시 저장된 메뉴를 불러와 카드를 생성
    lunch, dinner = make_meal_cards([restaurant], is_temp=True)

    # 식단 미리보기 응답 생성
    response = meal_response_maker(lunch, dinner)

    return response.get_json()


@app.post("/meal/submit")
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
    except Exception as e:  # pylint: disable=broad-exception-caught
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

    # 응답 반환
    return response.get_json()


if __name__ == "__main__":
    app.run()
