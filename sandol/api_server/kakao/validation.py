"""유효성 검사를 위한 함수들을 모아놓은 모듈"""
from .customerror import InvalidTypeError


def validate_type(
        allowed_types: tuple | object,
        *args,
        disallow_none: bool = False,
        exception_type=InvalidTypeError):
    """특정 타입에 대해 유효성 검사를 하는 함수

    허용할 타입을 allowed_types로 받아서, args에 대해 검사합니다.
    allowed_types는 튜플 형태로 여러 타입을 받을 수 있습니다.
    튜플이 아닌 단일 타입을 받을 수도 있습니다.
    disallow_none이 True일 경우 None이 들어오면 예외를 발생시킵니다.
    exception_type은 예외를 발생시킬 때 사용할 예외 타입을 지정합니다.

    Args:
        allowed_types (tuple | object): 허용할 타입
        args: 검사할 값들
        disallow_none (bool): None을 허용할지 여부
        exception_type: 예외 타입
    """
    if not isinstance(allowed_types, tuple):
        allowed_types = (allowed_types,)
    for value in args:
        if disallow_none and value is None:
            raise exception_type("None이어서는 안됩니다.")

        if value is not None and not isinstance(value, allowed_types):
            raise exception_type(f"{value}는 {allowed_types} 중 하나여야 합니다.")


def validate_str(*args, disallow_none: bool = False):
    """여러 인자에 대해 문자열인지 확인하는 함수

    validate_type 함수의 allowed_type을 str로 호출하는 함수로, 문자열인지 확인합니다.

    Args:
        args: 검사할 값들
        disallow_none (bool): None을 허용할지 여부
    """
    validate_type(str, *args, disallow_none=disallow_none)


def validate_int(*args, disallow_none: bool = False):
    """여러 인자에 대해 정수형인지 확인하는 함수

    validate_type 함수의 allowed_type을 int로 호출하는 함수로, 정수형인지 확인합니다.

    Args:
        args: 검사할 값들
        disallow_none (bool): None을 허용할지 여부
    """
    validate_type(int, *args, disallow_none=disallow_none)
