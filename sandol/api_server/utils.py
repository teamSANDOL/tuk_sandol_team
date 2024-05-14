"""API 서버에서 사용하는 유틸리티 함수들이 정의되어 있습니다.

주로 코드 중복을 줄이고 가독성을 높이기 위한 함수들이 정의되어 있습니다.
"""
import re

from .kakao.response import KakaoResponse, QuickReply
from .kakao.response.interactiron import ActionEnum
from .kakao.response.components import (
    CarouselComponent, TextCardComponent, SimpleTextComponent)
from ..crawler import RegistrationRestaurant


def split_string(s: str) -> list[str]:
    """문자열을 구분자를 기준으로 분리하여 리스트로 반환합니다.

    문자열을 받아 여러 구분자를 기준으로 분리하여 리스트로 반환합니다.
    구분자는 콤마, 세미콜론, 콜론, 파이프, 대시, 슬래시입니다.

    Args:
        s (str): 분리할 문자열

    Returns:
        list: 분리된 문자열 리스트
    """
    # 여러 구분자를 개행 문자로 변경
    delimiters = [r",\s*", r";", r":", r"\|", r"-", r"/"]
    regex_pattern = "|".join(delimiters)
    modified_str = re.sub(regex_pattern, "\n", s)

    # 개행 문자가 있는지 확인
    if "\n" in modified_str:
        # 개행 문자를 기준으로 분리하고, 각 항목의 양 끝 공백 제거
        return [
            item.strip() for item in modified_str.split("\n") if item.strip()
        ]
    else:
        # white-space를 기준으로 분리하고, 각 항목의 양 끝 공백 제거
        return [item.strip() for item in re.split(r"\s+", s) if item.strip()]


def make_meal_card(
    mealtype: str,
    restaurant: RegistrationRestaurant,
    is_temp=False
) -> TextCardComponent:
    """식당의 식단 정보를 TextCard 형식으로 반환합니다.

    식당 객체의 식단 정보를 받아 TextCardComponent 객체를 생성하여 반환합니다.
    만약 is_temp이 True일 경우 임시 메뉴를 사용합니다.
    만약 메뉴가 없을 경우 "식단 정보가 없습니다."를 반환합니다.

    Args:
        mealtype (str): "lunch" 또는 "dinner" 중 하나
        restaurant (RegistrationRestaurant): 식당 정보 객체
        is_temp (bool, optional): 임시 메뉴를 사용할지 여부. Defaults to False.
    """

    # is_temp가 True일 경우 임시 메뉴를 호출, 아닐 경우 일반 메뉴를 호출하기 위한 변수
    meal_attr = f"temp_{mealtype}" if is_temp else mealtype

    # 식사 종류를 한글로 변환하기 위한 딕셔너리
    mealtype_dict = {"lunch": "점심", "dinner": "저녁"}

    # 카드 제목
    title = f"{restaurant.name}({mealtype_dict[mealtype]})"  # 식당명(점심)

    # 메뉴 리스트를 개행문자로 연결하여 반환
    # "메뉴1\n메뉴2\n메뉴3" 또는 "식단 정보가 없습니다."
    menu_list: list = getattr(restaurant, meal_attr, [])
    description = "\n".join(
        menu_list) if menu_list else "식단 정보가 없습니다."

    return TextCardComponent(title=title, description=description)


def make_meal_cards(
    restaurants: list[RegistrationRestaurant], is_temp=False
) -> tuple[CarouselComponent, CarouselComponent]:
    """
    주어진 식당 목록에 대해 각각 점심과 저녁 식단 정보를 CarouselComponent로 반환합니다.
    카드 생성에는 make_meal_card 함수를 사용합니다.
    is_temp이 True일 경우 임시 메뉴를 사용합니다.

    Args:
        restaurants (list[Restaurant]): 식당 정보 리스트
        is_temp (bool, optional): 임시 메뉴를 사용할지 여부. Defaults to False.

    Returns:
        tuple[Carousel, Carousel]: 점심 Carousel, 저녁 Carousel
    """
    lunch = CarouselComponent()
    dinner = CarouselComponent()

    # 각 식당에 대해 점심과 저녁 식단 정보를 추가
    for restaurant in restaurants:
        lunch.add_item(make_meal_card("lunch", restaurant, is_temp))
        dinner.add_item(make_meal_card("dinner", restaurant, is_temp))

    return lunch, dinner


def meal_response_maker(
    lunch: CarouselComponent,
    dinner: CarouselComponent
) -> KakaoResponse:
    """식단 정보 미리보기를 반환하는 응답을 생성합니다.

    Args:
        lunch (CarouselComponent): 점심 식단 카드
        dinner (CarouselComponent): 저녁 식단 카드

    Returns:
        KakaoResponse: 식단 정보 미리보기 응답
    """
    # 임시 저장된 메뉴를 불러와 카드를 생성
    response = KakaoResponse()
    simple_text = SimpleTextComponent("식단 정보 미리보기")

    # 퀵리플라이 정의
    add_lunch_quick_reply = QuickReply(
        "점심 메뉴 추가", ActionEnum.BLOCK, block_id="660e009c30bfc84fad05dcbf")
    add_dinner_quick_reply = QuickReply(
        "저녁 메뉴 추가", ActionEnum.BLOCK, block_id="660e00a8d837db3443451ef9")
    submit_quick_reply = QuickReply(
        "확정", ActionEnum.BLOCK, block_id="661bccff4df3202baf9e8bdd")
    delete_menu_quick_reply = QuickReply(
        "메뉴 삭제", ActionEnum.BLOCK, block_id="66438b74334aaa30751802e9")
    delete_every_quick_reply = QuickReply(
        "모든 메뉴 삭제", ActionEnum.BLOCK, block_id="6643a2ce0431eb378ea12748")

    # 응답에 카드와 퀵리플라이 추가
    response = (
        response + simple_text + lunch + dinner +
        submit_quick_reply +
        add_lunch_quick_reply + add_dinner_quick_reply +
        delete_menu_quick_reply + delete_every_quick_reply)
    return response


def error_message(message: str | BaseException) -> TextCardComponent:
    """에러 메시지를 반환합니다.

    에러 메시지를 받아 추가 정보를 덧붙인 후 TextCardComponent로 반환합니다.
    만약 message가 BaseException 객체일 경우 문자열로 변환하여 사용합니다.

    Args:
        message (str): 에러 메시지
    """
    if isinstance(message, BaseException):
        message = str(message)
    message += "\n 죄송합니다. 서버 오류가 발생했습니다. 오류가 지속될 경우 관리자에게 문의해주세요."
    return TextCardComponent(title="오류 발생", description=message)


def handle_errors(func):
    """공통 오류 처리를 위한 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return KakaoResponse().add_component(error_message(e)).get_json()
    return wrapper
