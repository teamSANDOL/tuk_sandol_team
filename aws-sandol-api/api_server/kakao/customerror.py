class InvalidTypeError(ValueError):
    """유효하지 않은 타입에 대한 예외를 처리하는 클래스"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidLinkError(ValueError):
    """Link 형식에 대한 예외를 처리하는 클래스"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidActionError(ValueError):
    """유효하지 않은 action에 대한 예외를 처리하는 클래스"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidPayloadError(ValueError):
    """유효하지 않은 payload에 대한 예외를 처리하는 클래스"""

    def __init__(self, message: str):
        super().__init__(message)
