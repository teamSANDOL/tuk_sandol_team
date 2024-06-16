"""Sandol Service 팀의 패키지 입니다.

Api팀은 이 패키지를 사용하여 서버 개발을 진행합니다.
"""
from .cafeteria import Restaurant, get_meals


def get_registration(identification) -> Restaurant:
    """RegistrationRestaurant를 반환하는 함수

    Args:
        identification (str): 식당을 식별할 수 있는 id

    Returns:
        RegistrationRestaurant: id에 해당하는 RegistrationRestaurant 객체
    """
    return Restaurant.by_id(identification)


def get_view(identification):
    return Restaurant.by_id(identification)


__all__ = ["Restaurant", "get_meals"]
