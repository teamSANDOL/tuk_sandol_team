"""API 서버에서 사용하는 유틸리티 함수들이 정의되어 있습니다.

주로 코드 중복을 줄이고 가독성을 높이기 위한 함수들이 정의되어 있습니다.
"""

import os
import re
from typing import Literal, Optional
from functools import wraps
import traceback
from datetime import datetime, timedelta

from fastapi import Request
from fastapi.responses import JSONResponse
from kakao_chatbot import Payload
from kakao_chatbot.response import KakaoResponse
from kakao_chatbot.response.components import (
    ItemCardComponent,
    CarouselComponent,
    TextCardComponent,
    SimpleTextComponent,
    ListCardComponent,
)
import openpyxl

from crawler import Restaurant
from crawler.settings import KST, RESTAURANT_ACCESS_ID, SANDOL_ACCESS_ID
from crawler.ibookcrawler import BookTranslator
from crawler.ibookdownloader import BookDownloader
from api_server.settings import CAFETRIA_REGISTER_QUICK_REPLY_LIST, logger

from crawler.university_structure import (
    UniversityStructure,
    OrganizationUnit,
    OrganizationGroup,
    get_tukorea_structure,
)


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
        logger.error(f"Error: {e}")
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
        return [item.strip() for item in modified_str.split("\n") if item.strip()]
    else:
        # white-space를 기준으로 분리하고, 각 항목의 양 끝 공백 제거
        return [item.strip() for item in re.split(r"\s+", s) if item.strip()]


def get_korean_day(day):
    days = ["월", "화", "수", "목", "금", "토", "일"]
    return days[day]


def make_meal_card(
    mealtype: str, restaurant: Restaurant, is_temp=False
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
            f"{r_t.hour}시 업데이트"
        )
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
        block_id="672183965e0ed128077abfe3",
        extra={"restaurant_name": restaurant.name},
    )
    return textcard


def make_meal_cards(
    restaurants: list[Restaurant], is_temp=False
) -> tuple[CarouselComponent, CarouselComponent]:
    """주어진 식당 목록에 대해 각각 점심과 저녁 식단 정보를 CarouselComponent로 반환합니다.

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
    lunch: CarouselComponent, dinner: CarouselComponent
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


def make_org_group_list(
    group: OrganizationGroup,
) -> ListCardComponent | CarouselComponent:
    """조직 그룹 정보를 ListCardComponent 또는 CarouselComponent로 반환합니다.

    조직 그룹의 하위 조직 개수에 따라 ListCard 또는 Carousel을 생성합니다.
    - 5개 이하: 하나의 ListCardComponent에 모든 항목 추가
    - 6개 이상: 4개씩 ListCardComponent로 나누어 CarouselComponent에 추가

    Args:
        group (OrganizationGroup): 조직 그룹 객체
    """
    target_group = group.as_list()
    chunk_size = 4  # ListCard에 들어갈 최대 아이템 개수, CarouselComponent 사용 시 4개가 최대

    # 5개 이하일 경우, 하나의 ListCardComponent로 처리
    if len(target_group) <= 5:
        list_card = ListCardComponent(header=group.name)
        target_list = [list_card]
        chunk_size = 5 # CarouselComponent를 사용하지 않기 때문에 chunk_size를 5로 설정
    else:
        target_list = [
            ListCardComponent(header=group.name)
            for _ in range((len(target_group) + chunk_size - 1) // chunk_size)
        ]  # 4개씩 담을 ListCardComponent들 생성

    # 모든 unit을 순회하면서 적절한 ListCardComponent에 추가
    for idx, unit in enumerate(target_group):
        if isinstance(unit, OrganizationGroup):
            target_list[idx // chunk_size].add_item(
                title=unit.name,
                description="하위 조직 보기",
                action="message",
                message_text=f"{unit.name} 정보",
            )
        else:
            target_list[idx // chunk_size].add_item(
                title=unit.name,
                description="클릭해 정보보기",
                action="block",
                block_id="679ca1348c69ad7d00db038e",
                extra=unit.model_dump(),
            )

    return (
        target_list[0] if len(target_group) <= 5 else CarouselComponent(*target_list)
    )


def make_unit_item(unit: dict | OrganizationGroup) -> ItemCardComponent:
    """조직 단위 정보를 ItemCardComponent로 반환합니다.

    조직 단위 객체를 받아 ItemCardComponent 객체를 생성하여 반환합니다.
    ItemCardComponent 객체는 조직 단위의 이름과 전화번호를 보여줍니다.

    Args:
        unit (OrganizationUnit): 조직 단위 객체
    """
    if isinstance(unit, dict):
        logger.info(f"unit: {unit}")
        unit = OrganizationUnit.model_validate(unit, strict=False)

    item_card = ItemCardComponent(item_list=[], head=unit.name)
    if unit.phone:
        item_card.add_item(title="전화번호", description=unit.phone)
        item_card.add_button(label="전화 걸기", action="phone", phone_number=unit.phone)
    if unit.url:
        item_card.add_item(title="홈페이지", description=unit.url)
        item_card.add_button(
            label="홈페이지 방문", action="webLink", web_link_url=unit.url
        )
    if not unit.phone and not unit.url:
        item_card.add_item(
            title="정보 없음", description="전화번호 및 홈페이지 정보가 없습니다."
        )
    return item_card


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
        # exception_traceback = "".join(
        #     traceback.format_tb(message.__traceback__))

        detailed_message = (
            f"예외 타입: {exception_type}\n예외 메시지: {exception_message}\n"
            # f"트레이스백:\n{exception_traceback}"
        )
        message = detailed_message
    message += "\n죄송합니다. 서버 오류가 발생했습니다. 오류가 지속될 경우 관리자에게 문의해주세요."
    return TextCardComponent(title="오류 발생", description=message)


def check_access_id(id_type: Literal["restaurant", "sandol"] = "sandol"):
    """식당 혹은 산돌 ID 접근을 확인하는 데코레이터입니다."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            payload: Payload = kwargs.get("payload")
            if not payload:
                # 필요한 경우 args에서 Payload 인스턴스를 찾아 할당
                for arg in args:
                    if isinstance(arg, Payload):
                        payload = arg
                        break
            access_id = payload.user_id if payload else None

            logger.info(f"{id_type} 권한 접근 시도 access_id: {access_id}")

            response = KakaoResponse()
            response.add_component(SimpleTextComponent("접근 권한이 없습니다."))
            if (
                id_type == "restaurant"
                and access_id not in RESTAURANT_ACCESS_ID().keys()
            ) or (id_type == "sandol" and access_id not in SANDOL_ACCESS_ID().values()):
                return JSONResponse(response.get_dict())
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_tip_and_e(func):
    """TIP 가가식당과 E동 레스토랑 정보를 업데이트하는 데코레이터 입니다.

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
            hour=0, minute=0, second=0, microsecond=0
        )
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

        if os.path.exists(file_path):
            ibook = BookTranslator()
            tip = Restaurant.by_id("001")
            registration_time = get_last_saved_date(file_path)

            # 시간대 변환
            tip.registration_time = tip.registration_time.astimezone(tz=KST)
            registration_time = registration_time.astimezone(tz=KST)

            if registration_time < last_wednesday:
                must_download = True
            logger.info(f"tip.registration_time: {tip.registration_time.isoformat()}")
            logger.info(f"start_of_day: {start_of_day.isoformat()}")
            logger.info(f"registration_time: {registration_time.isoformat()}")
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


async def parse_payload(request: Request) -> Payload:
    """Request에서 Payload를 추출합니다.

    Request에서 JSON 데이터를 추출하여 Payload 객체로 변환합니다.
    FastAPI의 Dependency Injection을 사용하기 위한 함수입니다.
    """
    data_dict = await request.json()
    return Payload.from_dict(data_dict)


def create_openapi_extra(
    detail_params: Optional[dict] = None,
    client_extra: Optional[dict] = None,
    contexts: Optional[list] = None,
    utterance: Optional[str] = None,
) -> dict:
    """
    detail_params, client_extra, contexts를 받아
    OpenAPI 스키마에 맞게 변환하며, 각각을 default로 설정한다.
    예시:
    >>> detail_params = {
    ...     "Cafeteria": {
    ...         "origin": "산돌",
    ...         "value": "산돌식당"
    ...     }
    ... }
    """
    if detail_params is None:
        detail_params = {}
    if client_extra is None:
        client_extra = {}
    if contexts is None:
        contexts = []
    if utterance is None:
        utterance = ""

    detail_params_schema = {
        "type": "object",
        "additionalProperties": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "value": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "object"},
                    ]
                },
                "group_name": {"type": "string"},
            },
        },
        # detail_params를 그대로 default로 설정
        "default": detail_params,
    }
    default_params = {}
    if detail_params:
        default_params = {key: value["value"] for key, value in detail_params.items()}

    client_extra_schema = {
        "type": "object",
        "additionalProperties": {"type": "string"},
        # client_extra를 그대로 default로 설정
        "default": client_extra,
    }

    contexts_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "lifespan": {"type": "integer"},
                "ttl": {"type": ["integer", "null"]},
                "params": {
                    "type": "object",
                    "additionalProperties": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "string"},
                                    "resolved_value": {"type": "string"},
                                },
                            },
                        ],
                    },
                },
            },
        },
        # contexts를 그대로 default로 설정
        "default": contexts,
    }

    return {
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "intent": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "extra": {
                                        "type": "object",
                                        "properties": {
                                            "reason": {"type": "object"},
                                            "matched_knowledges": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "answer": {"type": "string"},
                                                        "question": {"type": "string"},
                                                        "categories": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                        "landing_url": {
                                                            "type": "string"
                                                        },
                                                        "image_url": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "required": ["id", "name"],
                            },
                            "user_request": {
                                "type": "object",
                                "properties": {
                                    "timezone": {
                                        "type": "string",
                                        "default": "Asia/Seoul",
                                    },
                                    "block": {
                                        "type": "object",
                                        "additionalProperties": True,
                                    },
                                    "utterance": {
                                        "type": "string",
                                        "default": utterance,
                                    },
                                    "lang": {"type": "string", "default": "ko"},
                                    "user": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "string",
                                                "default": "test_user_id",
                                            },
                                            "type": {
                                                "type": "string",
                                                "default": "botUserKey",
                                            },
                                            "properties": {
                                                "type": "object",
                                                "additionalProperties": True,
                                            },
                                        },
                                        "required": ["id", "type"],
                                    },
                                    "params": {
                                        "type": ["object", "null"],
                                        "additionalProperties": True,
                                    },
                                    "callback_url": {"type": ["string", "null"]},
                                },
                                "required": [
                                    "timezone",
                                    "block",
                                    "utterance",
                                    "lang",
                                    "user",
                                ],
                            },
                            "bot": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "default": "test_bot_id"},
                                    "name": {
                                        "type": "string",
                                        "default": "test_bot_name",
                                    },
                                },
                                "required": ["id", "name"],
                            },
                            "action": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "params": {
                                        "type": "object",
                                        "additionalProperties": {"type": "string"},
                                        "default": default_params,
                                    },
                                    "detailParams": detail_params_schema,
                                    "clientExtra": client_extra_schema,
                                },
                                "required": ["id", "name", "params"],
                            },
                            "contexts": contexts_schema,
                            "params": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                            "timezone": {"type": "string"},
                            "user": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string"},
                                    "properties": {
                                        "type": "object",
                                        "additionalProperties": True,
                                    },
                                },
                                "required": ["id", "type"],
                            },
                            "utterance": {"type": "string"},
                            "value": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                        },
                        "required": ["intent", "user_request", "bot", "action"],
                    }
                }
            },
        }
    }
