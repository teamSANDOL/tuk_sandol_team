# test.py파일
from flask import Flask, jsonify
from .crawler import Menu

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello Sandol"

@app.route("/meal_view")
def meal_view():
    output: dict = {
        "version": "2.0",
        "template": {
            "outputs": []
        }
    }

    restaurants = ["미가", "세미콘", "수호식당", "e동 교직원식당"]  # 식당 목록
    menu = Menu()  # Menu 객체 생성

    # 각 식당의 메뉴를 문자열로 변환
    lunch_menus = {restaurant: ', '.join(menu.get_lunch_menu(restaurant)) for restaurant in restaurants}
    dinner_menus = {restaurant: ', '.join(menu.get_dinner_menu(restaurant)) for restaurant in restaurants}

    in_cam = [{
        "simpleText": {
            "text": "교내식당 메뉴\n" + restaurants[2] + " [" + menu.date + "]\n중식 : " + lunch_menus[
                restaurants[2]] + "\n석식 : " + dinner_menus[restaurants[2]] + "\n\n" +
                    restaurants[3] + " [" + menu.date + "]\n중식 : " + lunch_menus[restaurants[3]] + "\n석식 : " +
                    dinner_menus[restaurants[3]]
        }  # 교내식당 메뉴 출력 , 추후 date 정보 추가 필요
    }]
    out_cam = [{
        "simpleText": {
            "text": "교외식당 메뉴\n" + restaurants[0] + " [" + menu.date + "]\n중식 : " + lunch_menus[
                restaurants[0]] + "\n석식 : " + dinner_menus[restaurants[0]] + "\n\n" +
                    restaurants[1] + " [" + menu.date + "]\n중식 : " + lunch_menus[restaurants[1]] + "\n석식 : " +
                    dinner_menus[restaurants[1]]
        }  # 교외식당 메뉴 출력 , 추후 date 정보 추가 필요
    }]

    output["template"]["outputs"] = in_cam + out_cam
    return jsonify(output)

app.run()
