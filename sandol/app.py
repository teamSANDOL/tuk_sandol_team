"""Sandol의 메인 애플리케이션 파일입니다."""
from flask import Flask, request

from sandol.api_server.kakao import KakaoResponse, SimpleTextComponent
from .crawler import get_registration, RegistrationRestaurant
from .api_server.kakao import Payload


app = Flask(__name__)


@app.route("/")
def root():
    """루트 페이지입니다."""
    return "Hello Sandol"


@app.post("/meal/register/<meal_type>")
def meal_register(meal_type: str):
    """식단 정보를 등록합니다.

    중식 및 석식 등록 발화시 호출되는 API입니다.
    """
    payload = Payload.from_dict(request.json)
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)
    print(request.json)
    print(restaurant.name)
    restaurant.clear_menu()
    restaurant.add_menu(meal_type, payload.detail_params["menu"].origin)
    print(restaurant.temp_menu, restaurant.lunch, restaurant.dinner)
    response = KakaoResponse()
    simpe_text = SimpleTextComponent("식단 정보 등록")
    return (response + simpe_text).get_json()


@app.post("/meal/register_menu")
def meal_register_menu():
    """식단 정보를 등록합니다.

    중식 및 석식 등록 발활 이후 메뉴 작성시 호출되는 API입니다.
    """
    payload = Payload.from_dict(request.json)
    restaurant: RegistrationRestaurant = get_registration(payload.user_id)

    restaurant.add_menu("lunch", payload.detail_params["menu"].origin)

    print(restaurant.temp_menu, restaurant.lunch, restaurant.dinner)
    response = KakaoResponse()
    simpe_text = SimpleTextComponent("식단 정보 등록")
    return (response + simpe_text).get_json()


if __name__ == "__main__":
    app.run()
