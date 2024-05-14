"""Sandol의 메인 애플리케이션 파일입니다."""
from flask import Flask, request

from .api_server.utils import make_meal_cards, split_string, error_message
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
    payload = Payload.from_dict(request.json)

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
    response = KakaoResponse()
    simple_text = SimpleTextComponent("식단 정보 등록")
    lunch, dinner = make_meal_cards([restaurant], is_temp=True)

    # 퀵리플라이 정의
    add_lunch_quick_reply = QuickReply(
        "중식 메뉴 추가", ActionEnum.BLOCK, block_id="660e009c30bfc84fad05dcbf")
    add_dinner_quick_reply = QuickReply(
        "석식 메뉴 추가", ActionEnum.BLOCK, block_id="660e00a8d837db3443451ef9")
    submit_quick_reply = QuickReply(
        "확정", ActionEnum.BLOCK, block_id="661bccff4df3202baf9e8bdd")

    # 응답에 카드와 퀵리플라이 추가
    response = (
        response + simple_text + lunch + dinner +
        submit_quick_reply + add_lunch_quick_reply + add_dinner_quick_reply)

    # 응답 반환
    return response.get_json()


@app.post("/meal/submit")
def meal_submit():
    """식단 정보를 확정하는 API입니다.

    임시 저장된 식단 정보를 확정하고 등록합니다.
    """

    # 요청을 받아 Payload 객체로 변환 및 사용자의 ID로 등록된 식당 객체를 불러옴
    payload = Payload.from_dict(request.json)
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
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
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
