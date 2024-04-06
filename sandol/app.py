# test.py파일
import json

from flask import Flask, jsonify, request

from .api_server.kakao import Payload
from .api_server.kakao.response import KakaoResponse
app = Flask(__name__)



with open('../crawler/CafeteriaInfo.json', 'r', encoding='UTF-8') as json_file:
    db = json.load(json_file)

# 메뉴 업데이트 함수
@app.route("/update_menu")
def update_menu(cafeteria_name, new_lunch_menu, new_dinner_menu):
    for restaurant in db:
        if restaurant['cafeteria_name'] == cafeteria_name:
            restaurant['lunch_menu'] = new_lunch_menu
            restaurant['dinner_menu']=new_dinner_menu
            break

@app.route("/")
def root():
    return "Hello Sandol"

@app.route("/meal_upload")
def meal_upload():
    assert request.json is not None
    cafeteria_input = Payload.from_dict(request.json)

    """
    # 사용자 인증 및 권한 확인
    user_id = user_input.user_id  # 사용자 ID를 가져옴
    # 사용자 ID로 사용자 권한 확인 및 식당 메뉴 수정자 여부 확인
    is_menu_modifier = check_user_permission(user_id)   # check_user_permission구현
    if not is_menu_modifier:
        return jsonify({"message": "메뉴 수정 권한이 없습니다."}), 403
    """


    # 요청에서 받은 데이터 처리
    assert request.json is not None
    user_input = Payload.from_dict(request.json)

    # 식당 이름과 업데이트할 메뉴 정보 가져오기
    cafeteria_name = user_input.parameters['cafeteria_name']
    meal_type = user_input.parameters['meal_type']
    new_menu = user_input.parameters['new_menu']

    # 메뉴 업데이트
    update_menu(cafeteria_name, meal_type, new_menu)

    # 업데이트된 메뉴 출력
    if meal_type == 'lunch':
        updated_menu = next(restaurant for restaurant in db if restaurant['cafeteria_name'] == cafeteria_name)[
            'lunch_menu']
    elif meal_type == 'dinner':
        updated_menu = next(restaurant for restaurant in db if restaurant['cafeteria_name'] == cafeteria_name)[
            'dinner_menu']

    return jsonify({"cafeteria_name": cafeteria_name, "updated_menu": updated_menu})


if __name__ == "__main__":
    app.run()
