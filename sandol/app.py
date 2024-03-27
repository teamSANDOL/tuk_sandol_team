from flask import Flask, jsonify

from .api_server import make_textcard
from .crawler import Restaurant, get_meals

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello Sandol"


@app.route("/meal/view")
def meal_view():
    """식단 정보를 Carousel TextCard 형태로 반환합니다."""
    restaurants: list[Restaurant] = get_meals()  # 식당 정보를 가져옵니다.

    # 출력 형식을 만듭니다.
    output: dict = {
        "version": "2.0",
        "template": {
            "outputs": []
        }
    }
    carousel = {
        "type": "TextCard",
        "items": []
    }

    on_cam = [{
        "simpleText": {
            "text": "교내 식당"
        }
    }]

    off_cam = [{
        "simpleText": {
            "text": "교외 식당"
        }
    }]

    # 식당 정보를 출력 형식에 맞게 변환합니다.
    for restaurant in restaurants:
        temp_carousel: dict = carousel.copy()

        # 식단 정보를 TextCard 형태로 변환합니다.
        lunch = make_textcard(
            title=f"{restaurant.name}(점심)",
            description="\n".join(restaurant.lunch)
        )
        dinner = make_textcard(
            title=f"{restaurant.name}(저녁)",
            description="\n".join(restaurant.dinner)
        )

        assert isinstance(temp_carousel["items"], list)
        # Carousel에 Card를 추가합니다.
        temp_carousel["items"].append(lunch)
        temp_carousel["items"].append(dinner)

        # Carousel을 출력 형식에 추가합니다.
        if restaurant.location == "교내":
            on_cam.append(temp_carousel)
        elif restaurant.location == "교외":
            off_cam.append(temp_carousel)
        else:
            raise ValueError(f"Invalid location: {restaurant.location}")

    output["template"]["outputs"] = on_cam + off_cam

    return jsonify(output)  # JSON 형태로 반환합니다.


app.run()
