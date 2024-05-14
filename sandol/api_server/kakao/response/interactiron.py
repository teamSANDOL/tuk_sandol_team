from enum import Enum
from typing import Any, Optional

from ..base import BaseModel
from ..customerror import InvalidActionError
from ..validation import validate_str, validate_type
from ..utils import camel_to_snake

__all__ = ["ActionEnum", "Interaction"]


class ActionEnum(Enum):
    """카카오톡 출력 요소의 버튼의 동작을 나타내는 열거형 클래스입니다.

    각 action 유형에 필요한 필드를 반환하는 required_field와 required_field_snake 속성을 가집니다.
    QuickReply와 Button의 action 속성에 사용됩니다.

    Attributes:
        required_field (str): 각 action 유형에 필요한 필드를 반환합니다.
        required_field_snake (str): 각 action 유형에 필요한 필드 값을 snake_case로 반환합니다.

    Returns:
        str: action 유형
    """
    WEBLINK = "webLink"
    MESSAGE = "message"
    PHONE = "phone"
    BLOCK = "block"
    SHARE = "share"
    OPERATOR = "operator"

    @property
    def required_fields(self) -> Optional[list[str]]:
        """각 action 유형에 필요한 필드를 반환합니다."""
        if self == ActionEnum.WEBLINK:
            return ['webLinkUrl']
        elif self == ActionEnum.MESSAGE:
            return ["messageText"]
        elif self == ActionEnum.PHONE:
            return ["phoneNumber"]
        elif self == ActionEnum.BLOCK:
            return ["blockId"]
        elif self == ActionEnum.SHARE:
            return None
        elif self == ActionEnum.OPERATOR:
            return None
        else:
            return None

    @property
    def required_fields_snake(self):
        """각 action 유형에 필요한 필드 값을 snake_case로 반환합니다."""
        camel_case_field = self.required_fields
        if camel_case_field is not None:
            return [camel_to_snake(field) for field in camel_case_field]
        return None


class Interaction(BaseModel):
    """카카오톡 출력 요소 Button과 QuickReply의 상위 클래스입니다.

    Button과 QuickReply의 공통 속성을 정의합니다.
    두 클래스의 공통 속성인 action, extra를 가집니다.
    두 클래스의 공통 메서드인 validate와 render를 정의합니다.

    Attributes:
        action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
        extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
    """
    available_action_enums: list[ActionEnum] = []  # Action 열거형의 리스트 오버라이드 필요

    def __init__(
            self,
            action: str | ActionEnum,
            extra: Optional[dict] = None):
        """Interaction 클래스의 생성자 메서드입니다.

        Args:
            action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
            extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
        """
        super().__init__()
        self.action = self.process_action(action)
        self.extra = extra

    @staticmethod
    def process_action(action: str | ActionEnum) -> ActionEnum:
        """문자열 또는 Action 열거형 인스턴스를 Action 열거형으로 변환합니다.

        action이 문자열인 경우 대문자로 변환하여 Action 열거형에 있는지 확인합니다.
        Action 열거형에 없는 경우 InvalidActionError를 발생시킵니다.

        Args:
            action (str | Action): QuickReply의 action

        Returns:
            Action: action을 나타내는 Action 열거형

        Raises:
            InvalidActionError: 유효하지 않은 action 값인 경우
        """
        validate_type(
            (str, ActionEnum),
            action,
            disallow_none=True,
            exception_type=InvalidActionError)

        # action이 문자열인 경우 Action 열거형으로 변환
        if isinstance(action, str):
            result = getattr(ActionEnum, action.upper(), None)
            if isinstance(result, ActionEnum):
                action = result
            else:
                raise InvalidActionError(f"유효하지 않은 action 값: {action}")
        return action

    def validate(self):
        """Interaction 객체의 유효성을 검사합니다.

        label이 문자열이 아닌 경우 InvalidTypeError를 발생시킵니다.
        action이 문자열 또는 Action 열거형이 아닌 경우 InvalidActionError를 발생시킵니다.
        이 클래스를 상속받는 클래스에서는 action에 따랄 필요한 필드의 타입을 검사해야 합니다.

        Raises:
            InvalidActionError: action이 문자열 또는 Action 열거형이 아닌 경우
        """

        validate_type(
            (str, ActionEnum),
            self.action,
            disallow_none=True,
            exception_type=InvalidActionError)

        # action이 ActionEnum에 있는지 확인
        if self.action not in self.available_action_enums:
            raise InvalidActionError(f"유효하지 않은 action 값: {self.action}")

        # action에 따라 필요한 필드가 있는경우 response에 저장
        if self.action.required_fields is not None:
            for field in self.action.required_fields_snake:
                validate_str(getattr(self, field))

        validate_type(dict, self.extra)

    def render(self) -> dict:
        """Interaction 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        Interaction 객체의 label, action, extra를 딕셔너리로 변환합니다.
        action에 따라 필요한 필드가 있는 경우 반환 값에 포함합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Interaction 딕셔너리
        """
        self.validate()
        response: dict[str, Any] = {
            "action": self.action.value,
        }

        # action에 따라 필요한 필드가 있는경우 response에 저장
        camels = self.action.required_fields
        snakes = self.action.required_fields_snake
        if camels is not None and snakes is not None:
            for camel, snake in zip(camels, snakes):
                response[camel] = getattr(self, snake)

        if self.extra is not None:
            response["extra"] = self.extra

        return self.remove_none_item(response)
