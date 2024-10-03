"""카카오톡 출력 요소 Button과 QuickReply 및 ListItem의 상위 클래스를 정의하는 모듈입니다.

이 모듈은 카카오톡 출력 요소 중 클릭시 Action을 취하는 역할을 하는
Button과 QuickReply 및 ListItem의 상위 클래스 Interaction을 정의합니다.

classes:
    ActionEnum: 카카오톡 출력 요소의 버튼의 동작을 나타내는 열거형 클래스
    Interaction: 카카오톡 출력 요소 Button과 QuickReply의 상위 클래스
"""
from enum import Enum
from typing import Any, Optional

from ..base import BaseModel
from ..customerror import InvalidActionError
from ..validation import validate_str, validate_type
from ..utils import camel_to_snake

__all__ = ["ActionEnum", "Interaction"]


class ActionEnum(Enum):
    """카카오톡 출력 요소의 버튼의 동작을 나타내는 열거형 클래스입니다.

    각 action 유형에 필요한 필드를 반환하는 uses_fields 속성을 가집니다.
    uses_fields 속성은 각 action 유형이 사용하는 필드를 반환합니다.

    Button과 QuickReply 및 ListItem의 action 속성에 사용됩니다.

    Methods:
        uses_fields (tuple[Optional[list[str]], Optional[list[str]]]):
            필요한 필드와 선택적 필드 목록을 반환하는 속성

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
    def uses_fields(self) -> tuple[Optional[list[str]], Optional[list[str]]]:
        """각 action 유형이 사용하는 필드를 반환합니다.

        각 action 유형에 필요한 필드와 선택적 필드를 반환합니다.
        tuple의 첫 번째 요소는 필요한 필드, 두 번째 요소는 선택적 필드입니다.
        필요한 필드와 선택적 필드가 없는 경우 각각 None을 반환합니다.

        Returns:
            tuple[Optional[list[str]], Optional[list[str]]]: 필요한 필드와 선택적 필드
        """
        if self == ActionEnum.WEBLINK:
            return ['webLinkUrl'], None
        elif self == ActionEnum.MESSAGE:
            return ["messageText"], None
        elif self == ActionEnum.PHONE:
            return ["phoneNumber"], None
        elif self == ActionEnum.BLOCK:
            return ["blockId"], ['messageText']
        elif self == ActionEnum.SHARE:
            return None, None
        elif self == ActionEnum.OPERATOR:
            return None, None
        else:
            return None, None


class Interaction(BaseModel):
    """카카오톡 출력 요소 Button과 QuickReply 및 ListItem의 상위 클래스입니다.

    세 출력 요소는 클릭시 Action을 취합니다. 이 클래스는 이들의 상위 클래스입니다.
    클릭시 취할 Action을 나타내는 action과 함께 전달할 데이터를 나타내는 extra를 가집니다.

    Button과 QuickReply, ListItem의 공통 속성을 정의합니다.
    클래스의 공통 속성인 action, extra를 가집니다.
    클래스의 공통 메서드인 validate와 render를 정의합니다.

    Classe Attributes:
        available_action_enums (list[ActionEnum]): 사용 가능한 Action 열거형의 리스트

    Attributes:
        action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
        extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
    """
    available_action_enums: list[ActionEnum] = []  # Action 열거형의 리스트 오버라이드 필요

    def __init__(
            self,
            action: Optional[str | ActionEnum],
            extra: Optional[dict] = None):
        """Interaction 클래스의 생성자 메서드입니다.

        action을 Action 열거형으로 변환하여 저장합니다.
        action이 None인 경우 None을 저장합니다.

        Args:
            action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
            extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
        """
        super().__init__()
        self.action = None
        if action is not None:
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

        action이 None인 경우 검사하지 않습니다.
        label이 문자열이 아닌 경우 InvalidTypeError를 발생시킵니다.
        action이 문자열 또는 Action 열거형이 아닌 경우 InvalidActionError를 발생시킵니다.
        이 클래스를 상속받는 클래스에서는 action에 따라 사용하는 필드의 타입을 검사해야 합니다.

        Raises:
            InvalidActionError: action이 문자열 또는 Action 열거형이 아닌 경우
        """

        validate_type(dict, self.extra)

        # action이 None인 경우 검사하지 않음
        if self.action is None:
            return None

        validate_type(
            (str, ActionEnum),
            self.action,
            disallow_none=True,
            exception_type=InvalidActionError)

        # action이 ActionEnum에 있는지 확인
        if self.action not in self.available_action_enums:
            raise InvalidActionError(f"유효하지 않은 action 값: {self.action}")

        # action에 따라 사용하는 필드가 있는경우 validate
        (
            required_fields,
            optional_fields
        ) = self.action.uses_fields

        if required_fields is not None:
            for field in required_fields:
                validate_str(
                    getattr(self, camel_to_snake(field)),
                    disallow_none=True)

        if optional_fields is not None:
            for field in optional_fields:
                validate_str(
                    getattr(self, camel_to_snake(field)))

    def render(self) -> dict:
        """Interaction 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        Interaction 객체의 label, action, extra를 딕셔너리로 변환합니다.
        action에 따라 필요한 필드가 있는 경우 반환 값에 포함합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Interaction 딕셔너리
        """
        # action이 None인 경우 빈 딕셔너리 반환
        if self.action is None:
            return {}

        self.validate()

        response: dict[str, Any] = {
            "action": self.action.value,
        }

        # action에 따라 필요한 필드가 있는경우 response에 저장
        (
            required_fields,
            optional_fields
        ) = self.action.uses_fields

        if required_fields is not None:
            for camel in required_fields:
                snake = camel_to_snake(camel)
                response[camel] = getattr(self, snake)

        if optional_fields is not None:
            for camel in optional_fields:
                snake = camel_to_snake(camel)
                if getattr(self, snake) is not None:
                    response[camel] = getattr(self, snake)

        if self.extra is not None:
            response["extra"] = self.extra

        return self.remove_none_item(response)
