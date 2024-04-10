"""카카오톡 출력 요소의 객체를 생성하는 클래스들을 정의한 모듈입니다.

class:
    Common: 카카오톡 출력 요소의 객체를 생성하는 추상 클래스입니다.
    Action: 카카오톡 출력 요소의 버튼의 동작을 나타내는 열거형 클래스입니다.
    QuickReply: 카카오톡 출력 요소 QuickReply의 객체를 생성하는 클래스입니다.
    QuickReplies: 카카오톡 출력 요소 QuickReplies의 객체를 생성하는 클래스입니다.
    Button: 카카오톡 출력 요소 Button의 객체를 생성하는 클래스입니다.
    Buttons: 카카오톡 출력 요소 Buttons의 객체를 생성하는 클래스입니다.
    Link: 카카오톡 출력 요소 Link의 객체를 생성하는 클래스입니다.
    Thumbnail: 카카오톡 출력 요소 Thumbnail의 객체를 생성하는 클래스입니다.
    Thumbnails: 카카오톡 출력 요소 Thumbnails의 객체를 생성하는 클래스입니다.
    Profile: 카카오톡 출력 요소 Profile의 객체를 생성하는 클래스입니다.
    ListItem: 카카오톡 출력 요소 ListCard의 items에 들어가는 Item을 나타내는 클래스입니다.
    ListItems: 카카오톡 출력 요소 ListCard의 items에 들어가는 Item들을 담는 클래스입니다.
"""
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Optional

from .validation import validate_str, validate_type
from .customerror import InvalidActionError, InvalidLinkError
from .base import BaseModel
from .utils import camel_to_snake


class Common(BaseModel, metaclass=ABCMeta):
    """카카오톡 출력 요소의 객체를 생성하는 추상 클래스입니다.

    스킬 응답의 template/context/data 중 context/data에 해당하는 객체가 이 클래스를 상속받아 구현됩니다.
    """

    @abstractmethod
    def render(self) -> dict | list:
        """객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다."""

    @abstractmethod
    def validate(self):
        """객체의 유효성을 검사합니다."""


class Action(Enum):
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
        if self == Action.WEBLINK:
            return ['webLinkUrl']
        elif self == Action.MESSAGE:
            return ["messageText", "blockId"]
        elif self == Action.PHONE:
            return ["phoneNumber"]
        elif self == Action.BLOCK:
            return ["blockId"]
        elif self == Action.SHARE:
            return None
        elif self == Action.OPERATOR:
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


class Link(Common):
    """카카오톡 출력 요소 Link의 객체를 생성하는 클래스

    Link는 버튼이나 썸네일 등에서 사용되는 링크를 나타냅니다.
    Link 객체는 웹, PC, 모바일 링크를 가질 수 있습니다.
    web이 가장 우선적으로 실행되며, web이 없는 경우에 플랫폼에 따라 PC 또는 모바일 링크가 실행됩니다.

    Args:
        web (Optional[str]): 웹 링크
        pc (Optional[str]): PC 링크
        mobile (Optional[str]): 모바일 링크

    example:
        >>> link = Link(web="https://www.example.com")
        >>> link.render()
        {'web': 'https://www.example.com'}
    """

    def __init__(
            self,
            web: Optional[str] = None,
            pc: Optional[str] = None,
            mobile: Optional[str] = None):
        self.web = web
        self.pc = pc
        self.mobile = mobile

    def validate(self):
        """Link 객체의 유효성을 검사합니다.

        Link는 최소 하나의 링크를 가져야 합니다.

        Raises:
            InvalidLinkError: Link는 최소 하나의 링크를 가져야 합니다.
        """
        if self.web is None and self.pc is None and self.mobile is None:
            raise InvalidLinkError("Link는 최소 하나의 링크를 가져야 합니다.")
        validate_str(self.web, self.pc, self.mobile)

    def render(self) -> dict:
        """Link 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        response에 web, pc, mobile 링크를 저장합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Link 딕셔너리
        """
        self.validate()
        response = {
            "web": self.web,
            "pc": self.pc,
            "mobile": self.mobile,
        }
        return self.remove_none_item(response)


class Thumbnail(Common):
    """카카오톡 출력 요소 Thumbnail의 객체를 생성하는 클래스

    BasicCard, CommerceCard 객체의 속성으로 사용됩니다.
    Thumbnail은 썸네일 이미지를 나타냅니다.
    썸네일 이미지는 이미지 URL을 가지며, 링크를 가질 수 있습니다.
    fixedRatio는 이미지의 비율을 고정할지 여부를 나타냅니다.

    Attributes:
        image_url (str): 썸네일 이미지 URL
        link (Link): 썸네일 이미지 클릭 시 이동할 링크
        fixed_ratio (bool): 이미지의 비율을 고정할지 여부
    """

    def __init__(
            self,
            image_url: str,
            link: Optional[Link] = None,
            fixed_ratio: bool = False):
        """Thumbnail 클래스의 생성자 메서드입니다.

        Args:
            image_url (str): 썸네일 이미지 URL
            link (Link): 썸네일 이미지 클릭 시 이동할 링크, 기본값은 None
            fixed_ratio (bool): 이미지의 비율을 고정할지 여부, 기본값은 False
        """
        self.image_url = image_url
        self.link = link
        self.fixed_ratio = fixed_ratio

    def validate(self):
        """Thumbnail 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: image_url이 문자열이 아닌 경우
            InvalidTypeError: link가 Link 객체가 아닌 경우
            InvalidTypeError: fixed_ratio가 bool이 아닌 경우
        """
        validate_str(self.image_url)
        validate_type(Link, self.link, disallow_none=False)
        validate_type(bool, self.fixed_ratio)

    def render(self) -> dict:
        """Thumbnail 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        response에 image_url, fixed_ratio, link를 저장합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Thumbnail 딕셔너리
        """
        self.validate()
        response = {
            "imageUrl": self.image_url,
            "fixedRatio": self.fixed_ratio,
            "link": self.link.render() if self.link is not None else None,
        }

        return self.remove_none_item(response)


class Profile(Common):
    """카카오톡 출력 요소 Profile의 객체를 생성하는 클래스

    Profile은 사용자의 프로필 정보를 나타냅니다.
    이미지 URL은 선택적으로 사용할 수 있습니다.
    이미지 사이즈는 180px X 180px이 권장됩니다.
    CommerceCard 객체의 속성으로 사용됩니다.
    ImageCard 객체의 속성으로 사용됩니다.

    Args:
        nickname (str): 사용자의 닉네임
        image_url (Optional[str]): 사용자의 프로필 이미지 URL, 기본값은 None
    """

    def __init__(self, nickname: str, image_url: Optional[str] = None):
        super().__init__()
        self.nickname = nickname
        self.image_url = image_url

    def validate(self):
        """Profile 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: nickname이 문자열이 아닌 경우
            InvalidTypeError: image_url이 문자열이 아닌 경우
        """
        validate_str(self.nickname, self.image_url)

    def render(self):
        """Profile 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Profile 딕셔너리
        """
        response = {
            "nickname": self.nickname,
            "imageUrl": self.image_url,
        }
        return self.remove_none_item(response)


class ListItem(Common):
    """카카오톡 출력 요소 ListCard의 items에 들어가는 Item을 나타내는 클래스

    ListItem은 리스트 형태의 정보를 나타냅니다.
    ListItem은 title, description, imageUrl, link, action, block_id,
    message_text, extra를 가질 수 있습니다.
    ListItems의 속성으로 사용됩니다.

    Args:
        title (str): header에 들어가는 경우, listCard의 제목, items에 들어가는 경우, 해당 항목의 제목
        description (Optional[str]): items에 들어가는 경우, 해당 항목의 설명
        image_url (Optional[str]): items에 들어가는 경우, 해당 항목의 우측 안내 사진
        link (Optional[Link]): 리스트 아이템 클릭 시 동작할 링크
        action (Optional[str | Action]): 리스트 아이템 클릭시 수행될 작업(block 또는 message)
        block_id (Optional[str]): action이 block인 경우 block_id를 갖는 블록을 호출
        message_text (Optional[str]): action이 message인 경우 리스트 아이템 클릭 시 전달할 메시지
        extra (Optional[dict]): 블록 호출시, 스킬 서버에 추가적으로 제공하는 정보
    """

    def __init__(
            self,
            title: str,
            description: Optional[str] = None,
            image_url: Optional[str] = None,
            link: Optional[Link] = None,
            action: Optional[str | Action] = None,
            block_id: Optional[str] = None,
            message_text: Optional[str] = None,
            extra: Optional[dict] = None):
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url
        self.link = link
        self.action = action
        self.block_id = block_id
        self.message_text = message_text
        self.extra = extra

    def validate(self):
        """ListItem 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: title이 문자열이 아니거나 None인 경우
            InvalidTypeError: description이 문자열이 아닌 경우
            InvalidTypeError: image_url이 문자열이 아닌 경우
            InvalidTypeError: link가 Link 객체가 아닌 경우
        """
        validate_str(self.title, disallow_none=True)
        validate_str(
            self.description, self.image_url,
            self.block_id, self.message_text)
        validate_type(Link, self.link)

    def render(self):
        """ListItem 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 ListItem 딕셔너리
        """
        self.validate()
        response = {
            "title": self.title,
            "description": self.description,
            "imageUrl": self.image_url,
            "link": self.link.render() if self.link is not None else None,
            "action": self.action,
            "blockId": self.block_id,
            "messageText": self.message_text,
        }
        return self.remove_none_item(response)


class ListItems(Common):
    """카카오톡 출력 요소 ListCard의 items에 들어가는 Item들을 담는 클래스

    ListItems는 ListItem 객체들의 리스트를 나타냅니다.
    ListCard 객체의 속성으로 사용됩니다.

    Args:
        list_items (list[ListItem]): ListItem 객체들의 리스트, 기본값은 빈 리스트
        max_list_items (int): ListItem의 최대 개수, 기본값은 5
    """

    def __init__(
            self,
            list_items: Optional[list[ListItem]] = None,
            max_list_items: int = 5):
        super().__init__()
        if list_items is None:
            list_items = []
        self._list_items = list_items
        self.max_list_items = max_list_items

    def validate(self):
        """ListItems 객체의 유효성을 검사합니다.

        ListItem의 개수가 최대 개수를 초과하는 경우 ValueError를 발생시킵니다.

        Raises:
            ValueError: ListItem의 개수가 최대 개수를 초과하는 경우
        """
        if len(self._list_items) > self.max_list_items:
            raise ValueError(
                f"버튼이 최대 {self.max_list_items}개까지 가능하도록 제한되어 있습니다.")
        validate_type(ListItem, *self._list_items)

    def add_item(self, list_item: ListItem):
        """ListItem을 추가합니다.

        Args:
            list_item (ListItem): 추가할 ListItem 객체

        Raise:
            ValueError: 이미 최대 버튼 개수에 도달한 경우
        """
        if len(self._list_items) > self.max_list_items:
            raise ValueError(
                f"버튼이 최대 {self.max_list_items}개까지 가능하도록 제한되어 있습니다.")
        validate_type(ListItem, list_item)
        self._list_items.append(list_item)

    def remove_item(self, list_item: ListItem):
        """ListItem을 삭제합니다.

        Args:
            list_item (ListItem): 삭제할 ListItem 객체

        Raise:
            ValueError: 버튼이 존재하지 않는 경우
        """
        if list_item not in self._list_items:
            raise ValueError("해당 ListItem이 존재하지 않습니다.")
        self._list_items.remove(list_item)

    def render(self):
        """ListItems 객체를 카카오톡 응답 형식에 맞게 리스트로 변환합니다.

        ListItems 객체의 각 ListItem 객체를 render 메서드를 통해 변환하고,
        변환된 ListItem 객체들을 리스트로 반환합니다.

        Returns:
            list: 카카오톡 응답 형식에 맞게 변환된 ListItem 객체의 리스트
        """
        self.validate()
        return [list_item.render() for list_item in self._list_items]

    @property
    def is_empty(self) -> bool:
        """ListItems 객체가 비어있는지 여부를 반환합니다.

        Returns:
            bool: ListItems 객체가 비어있는지 여부
        """
        return len(self._list_items) == 0


class Interaction(Common):
    """카카오톡 출력 요소 Button과 QuickReply의 상위 클래스입니다.

    Button과 QuickReply의 공통 속성을 정의합니다.
    두 클래스의 공통 속성인 label, action, extra를 가집니다.
    두 클래스의 공통 메서드인 validate와 render를 정의합니다.

    Attributes:
        label (str): 사용자에게 보여질 버튼의 텍스트
        action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
        extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
    """
    available_actions: list[Action] = []  # Action 열거형의 리스트 오버라이드 필요

    def __init__(
            self,
            label: str,
            action: str | Action,
            extra: Optional[dict] = None):
        """Interaction 클래스의 생성자 메서드입니다.

        Args:
            label (str): 사용자에게 보여질 버튼의 텍스트
            action (str | Action): 버튼의 동작, 문자열 또는 Action 열거형
            extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
        """
        super().__init__()
        self.label = label
        self.action = self.process_action(action)
        self.extra = extra

    @staticmethod
    def process_action(action: str | Action) -> Action:
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
            (str, Action),
            action,
            disallow_none=True,
            exception_type=InvalidActionError)

        # action이 문자열인 경우 Action 열거형으로 변환
        if isinstance(action, str):
            result = getattr(Action, action.upper(), None)
            if isinstance(result, Action):
                action = result
            else:
                raise InvalidActionError(f"유효하지 않은 action 값: {action}")
        return action

    def validate(self):
        """Interaction 객체의 유효성을 검사합니다.

        label이 문자열이 아닌 경우 InvalidTypeError를 발생시킵니다.
        action이 문자열 또는 Action 열거형이 아닌 경우 InvalidActionError를 발생시킵니다.

        Raises:
            InvalidTypeError: label이 문자열이 아닌 경우
            InvalidActionError: action이 문자열 또는 Action 열거형이 아닌 경우
        """
        validate_str(self.label)

        validate_type(
            (str, Action),
            self.action,
            disallow_none=True,
            exception_type=InvalidActionError)

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
            "label": self.label,
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


class QuickReply(Interaction):
    """카카오톡 출력 요소 QuickReply의 객체를 생성하는 클래스입니다.

    QuickReply(바로가기)는 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    quickReplies(바로가기 버튼리스트가 담긱 객체)의 속성으로 사용됩니다.

    Args:
        label (str): 사용자에게 보여질 버튼의 텍스트
        action (str | Action): 바로가기 응답의 기능, 문자열 또는 Action 열거형, 기본값은 "Message"
        message_text (str | None): action이 "Message"인 경우 사용자가 챗봇에게 전달할 메시지
        block_id (str | None): action이 "Block"인 경우 호출할 블록의 ID
        extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터

    example:
        >>> quick_reply = QuickReply(
        ...     label="바로가기 1",
        ...     action="message",
        ...     message_text="바로가기 1 클릭"
        ... )
        >>> quick_reply.render()
        {'label': '바로가기 1', 'action': 'message', 'messageText': '바로가기 1 클릭'}
    """
    available_actions: list[Action] = [Action.MESSAGE, Action.BLOCK]

    def __init__(
            self,
            label: str,
            action: str | Action = "Message",
            message_text: Optional[str] = None,
            block_id: Optional[str] = None,
            extra: Optional[dict] = None):
        """QuickReply 클래스의 생성자 메서드입니다.

        Args:
            label (str): 사용자에게 보여질 버튼의 텍스트
            action (str | Action, optional): 바로가기 응답의 기능, 문자열 또는 Action 열거형,
                                                기본값은 "Message"
            message_text (str, optional): action이 "Message"인 경우
                                            사용자가 챗봇에게 전달할 메시지, 기본값은 None
            block_id (str, optional): action이 "Block"인 경우 호출할 블록의 ID, 기본값은 None
            extra (dict, optional): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터, 기본값은 None
        """
        super().__init__(label=label, action=action, extra=extra)
        self.message_text = message_text
        self.block_id = block_id

    def validate(self):
        """QuickReply 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: message_text가 문자열이 아닌 경우
            InvalidTypeError: block_id가 문자열이 아닌 경우
        """
        validate_str(self.message_text, self.block_id)
        super().validate()


class Button(Interaction):
    """카카오톡 출력 요소 Button의 객체를 생성하는 클래스

    Button은 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    Buttons 객체의 속성으로 사용됩니다.

    Attributes:
        label (str): 버튼의 텍스트
        action (Action): 버튼의 동작
        web_link_url (str): 웹 링크
        message_text (str): 메시지
        phone_number (str): 전화번호
        block_id (str): 블록 ID
        extra (dict): 스킬 서버에 추가로 전달할 데이터

    Raises:
        ValueError: text가 문자열이 아닌 경우

    example:
        >>> button = Button(
        ...     label="버튼 1",
        ...     action="message",
        ...     message_text="버튼 1 클릭"
        ... )
        >>> button.render()
        {'label': '버튼 1', 'action': 'message', 'messageText': '버튼 1 클릭'}
    """
    available_actions: list[Action] = [action for action in Action]

    def __init__(
            self,
            label: str,
            action: str | Action,
            web_link_url: Optional[str] = None,
            message_text: Optional[str] = None,
            phone_number: Optional[str] = None,
            block_id: Optional[str] = None,
            extra: Optional[dict] = None):
        """Button 클래스의 생성자 메서드입니다.

        Args:
            label (str): 버튼에 적히는 문구입니다.
            action (str | Action): 버튼 클릭시 수행될 작업입니다.
                                    (webLink, message, phone,
                                    block, share, operator)
            web_link_url (Optional[str]): 웹 브라우저를 열고 이동할 주소입니다.
                                            (action이 webLink일 경우 필수)
            message_text (Optional[str]): action이 message인 경우 사용자의 발화로
                                            messageText를 내보냅니다. (이 경우 필수)
                                        action이 block인 경우 블록 연결시
                                            사용자의 발화로 노출됩니다. (이 경우 필수)
            phone_number (Optional[str]): 전화번호 (action이 phone일 경우 필수)
            block_id (Optional[str]): 호출할 block_id. (action이 block일 경우 필수)
            extra (Optional[dict]): 스킬 서버에 추가로 전달할 데이터
            """

        super().__init__(label, action, extra)
        self.web_link_url = web_link_url
        self.message_text = message_text
        self.phone_number = phone_number
        self.block_id = block_id

    def validate(self):
        """Button 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: web_link_url이 문자열이 아닌 경우
            InvalidTypeError: message_text가 문자열이 아닌 경우
            InvalidTypeError: phone_number가 문자열이 아닌 경우
            InvalidTypeError: block_id가 문자열이 아닌 경우
        """
        validate_str(
            self.web_link_url,
            self.message_text,
            self.phone_number,
            self.block_id)
        super().validate()


if __name__ == "__main__":
    testbutton = Button(
        label="구경하기",
        action="webLink",
        web_link_url="https://sio2.pe.kr/login",
        message_text=None)
    print(testbutton.render())
