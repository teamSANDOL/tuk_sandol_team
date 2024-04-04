
from flask import Flask, request


from .api_server import HELP, CAFETERIA_WEB, make_meal_cards
from .api_server.kakao import Payload
from .api_server.kakao.response import KakaoResponse
from .api_server.kakao.skill import TextCard
from .crawler import Restaurant, get_meals

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello Sandol"


@app.post("/meal/view")
def meal_view():
    """식단 정보를 Carousel TextCard 형태로 반환합니다."""
    assert request.json is not None
    payload = Payload.from_dict(request.json)  # 요청 Payload를 파싱합니다.

    # payload에서 cafeteria 값 추출
    cafeteria = getattr(payload.params, "식당", None) or getattr(
        payload.params, "cafeteria", None)

    # 식당 정보를 가져옵니다.
    restaurants: list[Restaurant] = get_meals()

    # cafeteria 값이 있을 경우 해당 식당 정보로 필터링
    if cafeteria:
        if cafeteria.value in ["미가", "세미콘", "수호"]:
            # 식단 정보를 해당 식당 정보로 필터링
            restaurants = [r for r in restaurants if r.name == cafeteria.value]
        else:
            # TIP 또는 E동 식당인 경우
            return CAFETERIA_WEB.get_json()

    # 점심과 저녁 메뉴를 담은 Carousel 생성
    lunch_carousel, dinner_carousel = make_meal_cards(restaurants)

    response = KakaoResponse()  # 응답 객체 생성

    # 점심과 저녁 메뉴 Carousel을 SkillList에 추가
    # 모듈에서 자동으로 비어있는 Carousel은 추가하지 않음
    response.add_skill(lunch_carousel)
    response.add_skill(dinner_carousel)
    if not cafeteria or cafeteria.value not in ["미가", "세미콘", "수호"]:
        response.add_skill(CAFETERIA_WEB)

    # 식단 정보가 없는 경우 정보 없음 TextCard 추가
    if response.is_empty:
        response.add_skill(TextCard("식단 정보가 없습니다."))

    # 도움말 추가
    response.add_quick_reply(HELP)

    return response.get_json()


if __name__ == "__main__":
    app.run()
