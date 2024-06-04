"""API 서버에서 사용하는 유틸리티 함수들이 정의되어 있습니다.

주로 코드 중복을 줄이고 가독성을 높이기 위한 함수들이 정의되어 있습니다.
"""
from datetime import datetime, timedelta
import os
import re
from functools import wraps
import traceback

import openpyxl

from api_server.settings import CAFETRIA_REGISTER_QUICK_REPLY_LIST
from api_server.kakao.response.components.card import ItemCardComponent
from api_server.kakao.response import KakaoResponse
from api_server.kakao.response.components import (
    CarouselComponent, TextCardComponent, SimpleTextComponent)
from crawler import Restaurant
from crawler.settings import KST
from crawler.ibookcrawler import BookTranslator
from crawler.ibookdownloader import BookDownloader


def get_last_saved_date(filepath: str) -> datetime:
    """Excel 파일의 마지막으로 저장된 날짜를 반환합니다.

    Excel 파일의 경로를 받아 마지막으로 저장된 날짜를 반환합니다.
    만약 파일이 없는 등 예외가 발생할 경우 현재 시간에서 7일 전으로 설정합니다.

    Args:
        filepath (str): Excel 파일 경로

    Returns:
        datetime: 마지막으로 저장된 날짜
    """
    try:
        # Excel 파일 열기
        workbook = openpyxl.load_workbook(filepath, read_only=True)
        # 마지막으로 저장된 날짜 가져오기
        last_saved = workbook.properties.modified
        return last_saved.astimezone(KST)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}")
        return datetime.now(tz=KST) - timedelta(days=7)


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


def get_korean_day(day):
    days = ["월", "화", "수", "목", "금", "토", "일"]
    return days[day]


def make_meal_card(
    mealtype: str,
    restaurant: Restaurant,
    is_temp=False
) -> ItemCardComponent | TextCardComponent:
    """식당의 식단 정보를 TextCard 형식으로 반환합니다.

    식당 객체의 식단 정보를 받아 TextCardComponent 객체를 생성하여 반환합니다.
    만약 is_temp이 True일 경우 임시 메뉴를 사용합니다.
    만약 메뉴가 없을 경우 "식단 정보가 없습니다."를 반환합니다.

    Args:
        mealtype (str): "lunch" 또는 "dinner" 중 하나
        restaurant (Restaurant): 식당 정보 객체
        is_temp (bool, optional): 임시 메뉴를 사용할지 여부. Defaults to False.
    """

    # is_temp가 True일 경우 임시 메뉴를 호출, 아닐 경우 일반 메뉴를 호출하기 위한 변수
    meal_attr = f"temp_{mealtype}" if is_temp else mealtype

    # 식사 종류를 한글로 변환하기 위한 딕셔너리
    mealtype_dict = {"lunch": "점심", "dinner": "저녁"}

    # 카드 제목
    title = f"{restaurant.name}({mealtype_dict[mealtype]})"  # 식당명(점심)
    r_t: datetime = restaurant.registration_time
    formatted_time = r_t.strftime(
        (
            f"\n{r_t.month}월 {r_t.day}일 {get_korean_day(r_t.weekday())}요일 "
            f"{r_t.hour}시 업데이트")
    )

    # 메뉴 리스트를 개행문자로 연결하여 반환
    # "메뉴1\n메뉴2\n메뉴3" 또는 "식단 정보가 없습니다."
    menu_list: list = getattr(restaurant, meal_attr, [])

    # TODO(Seokyoung_Hong): ItemCardComponent를 사용할 경우의 코드, 사용여부 결정 후 삭제
    # response = ItemCardComponent([])
    # response.image_title = ImageTitle(
    #     title=title,
    #     description=formatted_time,
    # )

    # if menu_list:
    #     for menu in menu_list:
    #         response.add_item(
    #             title="메뉴",
    #             description=menu
    #         )
    # else:
    #     response.add_item(
    #         title="메뉴",
    #         description="식단 정보가 없습니다."
    #     )
    # response.add_button(
    #     label="식당 정보 보기",
    #     action="block",
    #     block_id="665ca91ba99186411b75b8c9",
    #     extra={
    #         "restaurant_name": restaurant.name
    #     }
    # )

    # return response

    description = "\n".join(menu_list) if menu_list else "식단 정보가 없습니다."

    description += formatted_time
    textcard = TextCardComponent(title=title, description=description)
    textcard.add_button(
        label="식당 정보 보기",
        action="block",
        block_id="665ca91ba99186411b75b8c9",
        extra={
            "restaurant_name": restaurant.name
        }
    )
    return textcard


def make_meal_cards(
    restaurants: list[Restaurant], is_temp=False
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


def meal_error_response_maker(message: str) -> KakaoResponse:
    """식단 정보 에러 메시지를 반환하는 응답을 생성합니다.

    Args:
        message (str): 에러 메시지

    Returns:
        KakaoResponse: 에러 메시지 응답
    """
    response = KakaoResponse()
    simple = SimpleTextComponent(message)
    response.add_component(simple)
    for quick_reply in CAFETRIA_REGISTER_QUICK_REPLY_LIST:
        response.add_quick_reply(quick_reply)

    return response


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
    response = KakaoResponse() + SimpleTextComponent("식단 미리보기") + lunch + dinner
    for quick_reply in CAFETRIA_REGISTER_QUICK_REPLY_LIST:
        response.add_quick_reply(quick_reply)
    return response


def error_message(message: str | BaseException) -> TextCardComponent:
    """에러 메시지를 반환합니다.

    에러 메시지를 받아 추가 정보를 덧붙인 후 TextCardComponent로 반환합니다.
    만약 message가 BaseException 객체일 경우 문자열로 변환하여 사용합니다.

    Args:
        message (str): 에러 메시지
    """
    if isinstance(message, BaseException):
        exception_type = type(message).__name__
        exception_message = str(message)
        exception_traceback = "".join(  # TODO(Seokyoung_Hong): 베포시 주석 처리
            traceback.format_tb(message.__traceback__))

        detailed_message = (
            f"예외 타입: {exception_type}\n"
            f"예외 메시지: {exception_message}\n"
            f"트레이스백:\n{exception_traceback}"  # TODO(Seokyoung_Hong): 베포시 주석 처리
        )
        message = detailed_message
    message += "\n죄송합니다. 서버 오류가 발생했습니다. 오류가 지속될 경우 관리자에게 문의해주세요."
    return TextCardComponent(title="오류 발생", description=message)


def check_tip_and_e(func):
    """TIP 가가식당과 E동 레스토랑 정보를 업데이트하는 데코레이터

    data.xlsx 파일의 수정 시간을 확인하여 지난 주 수요일 이전에 업데이트된 경우
    data.xlsx 파일을 다운로드하고, TIP 가가식당과 E동 레스토랑 정보를 업데이트합니다.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Lambda 환경에서 /tmp 디렉토리를 사용
        file_path = "/tmp/data.xlsx"

        must_download = False

        today = datetime.now(tz=KST)
        # 지난 주 수요일 날짜 계산
        if today.weekday() >= 2:
            last_wednesday = today - timedelta(days=today.weekday() - 2 + 7)
        else:
            last_wednesday = today - timedelta(days=today.weekday() - 2 + 14)

        # 시간, 분, 초, 마이크로초를 0으로 설정
        last_wednesday = last_wednesday.replace(
            hour=0, minute=0, second=0, microsecond=0)
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

        if os.path.exists(file_path):
            ibook = BookTranslator()
            tip = Restaurant.by_id("001")
            registration_time = get_last_saved_date(file_path)

            if registration_time < last_wednesday:
                must_download = True
        else:
            must_download = True

        if must_download:
            downloader = BookDownloader()
            downloader.get_file(file_path)  # data.xlsx에 파일 저장

        if must_download or tip.registration_time < start_of_day:
            # 식단 정보 test.json에 저장
            ibook = BookTranslator()
            ibook.submit_tip_info()
            ibook.submit_e_info()
        return await func(*args, **kwargs)
    return wrapper
