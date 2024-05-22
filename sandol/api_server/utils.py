"""API 서버에서 사용하는 유틸리티 함수들을 정의합니다."""
from sandol.crawler.cafeteria_view import Restaurant
from .kakao.response.components import CarouselComponent, TextCardComponent


def make_meal_cards(
    restaurants: list[Restaurant]
) -> tuple[CarouselComponent, CarouselComponent]:
    """
    주어진 식당 목록에 대해 TextCard들을 생성하여
    점심 Carousel과 저녁 Carousel을 생성합니다.

    Args:
        restaurants (list[Restaurant]): 식당 정보 리스트

    Returns:
        tuple[Carousel, Carousel]: 점심 Carousel, 저녁 Carousel
    """
    lunch = CarouselComponent()
    dinner = CarouselComponent()
    for restaurant in restaurants:

        if restaurant.lunch:  # 점심 식단 정보가 있을 경우에만 추가
            lunch.add_item(TextCardComponent(
                title=f"{restaurant.name}(점심)",
                description="\n".join(restaurant.lunch)
            ))
        if restaurant.dinner:  # 저녁 식단 정보가 있을 경우에만 추가
            dinner.add_item(TextCardComponent(
                title=f"{restaurant.name}(저녁)",
                description="\n".join(restaurant.dinner)
            ))
    return lunch, dinner
