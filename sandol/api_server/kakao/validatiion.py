from .customerror import InvalidTypeError


def validate_type(
        allowed_types: tuple | object,
        *args,
        disallow_none: bool = False,
        exception_type=InvalidTypeError):
    """특정 타입에 대해 유효성 검사를 하는 함수"""
    if not isinstance(allowed_types, tuple):
        allowed_types = (allowed_types,)
    for value in args:
        if disallow_none and value is None:
            raise exception_type("None이어서는 안됩니다.")

        if value is not None and not isinstance(value, allowed_types):
            raise exception_type(f"{value}는 {allowed_types} 중 하나여야 합니다.")


def validate_str(*args, disallow_none: bool = False):
    """여러 인자에 대해 문자열인지 확인하는 함수"""
    validate_type(str, *args, disallow_none=disallow_none)


def validate_int(*args, disallow_none: bool = False):
    """여러 인자에 대해 정수형인지 확인하는 함수"""
    validate_type(int, *args, disallow_none=disallow_none)