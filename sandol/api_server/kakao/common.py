from abc import ABCMeta
from enum import Enum
from typing import Optional, overload

from .validatiion import validate_str, validate_type
from .customerror import InvalidActionError, InvalidTypeError, InvalidLinkError
from .base import BaseModel


class Common(BaseModel, metaclass=ABCMeta):
    """카카오톡 응답 형태의 객체를 생성하는 추상 클래스

    스킬 응답의 template/context/data 중 context/data에 해당하는 객체가 이 클래스를 상속받아 구현됩니다.

    Attributes:
        response_content_obj (dict): 카카오톡 응답 형태의 객체가 저장되는 딕셔너리, 빈 딕셔너리로 초기화됩니다.
    """

    def __init__(self):
        self.response_content_obj: dict | list = {}


class Action(Enum):
    """Action 열거형 클래스

    카카오톡 응답 형태의 버튼의 동작을 나타내는 열거형 클래스입니다.
    Button과 QuickReply 클래스에서 사용됩니다.

    Args:
        WEBLINK (str): 웹 브라우저를 열고 webLinkUrl 의 주소로 이동
        MESSAGE (str): 사용자의 발화로 messageText를 실행
        PHONE (str): phoneNumber에 있는 번호로 전화
        BLOCK (str): blockId를 갖는 블록을 호출
        SHARE (str): 말풍선을 다른 유저에게 공유
        OPERATOR (str): 상담원 연결
    """
    WEBLINK = "webLink"
    MESSAGE = "message"
    PHONE = "phone"
    BLOCK = "block"
    SHARE = "share"
    OPERATOR = "operator"


class QuickReply(Common):
    """카카오톡 응답 형태 QuickReply의 객체를 생성하는 클래스

    QuickReply는 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    quickReplies(바로가기 버튼들)의 버튼으로 사용되며,
    QuickReplies 객체의 속성으로 사용됩니다.

    Args:
        label (str): 사용자에게 보여질 버튼의 텍스트
        action (str | Action): 바로가기 응답의 기능, 문자열 또는 Action 열거형, 기본값은 "Message"
        messageText (str | None): action이 "Message"인 경우 사용자가 챗봇에게 전달할 메시지
        blockId (str | None): action이 "Block"인 경우 호출할 블록의 ID
        extra (dict | None): 블록을 호출 시 스킬 서버에 추가로 전달할 데이터
    """
    # QuickReply의 action에 따라 필요한 필드를 매핑하는 딕셔너리
    action_field_map = {Action.MESSAGE: "messageText", Action.BLOCK: "blockId"}

    def __init__(
            self,
            label: str,
            action: str | Action = "Message",
            messageText: Optional[str] = None,
            blockId: Optional[str] = None,
            extra: Optional[dict] = None):
        super().__init__()
        self.label = label
        self.action = self.process_action(action)
        self.messageText = messageText
        self.blockId = blockId
        self.extra = extra

    @staticmethod
    def process_action(action: str | Action) -> Action:
        """문자열 또는 Action 열거형 인스턴스를 Action 열거형으로 변환합니다.

        action이 문자열인 경우 대문자로 변환하여 Action 열거형에 있는지 확인합니다.
        Action 열거형에 없는 경우 InvalidActionError를 발생시킵니다.

        Args:
            action (str | Action): QuickReply의 action

        Returns:
            Action: QuickReply의 action을 나타내는 Action 열거형

        Raises:
            InvalidActionError: 유효하지 않은 action 값인 경우
        """
        validate_type(
            (str, Action),
            action,
            disallow_none=True,
            exception_type=InvalidActionError)

        if isinstance(action, str):
            # getattr을 사용하여 안전하게 Action 열거형에 접근
            result = getattr(Action, action.upper(), None)
            if result is None:
                raise InvalidActionError(f"유효하지 않은 action 값: {action}")
            return result

        return action

    def validate(self):
        """QuickReply 객체의 유효성을 검사합니다.

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

    def render(self) -> dict:
        """QuickReply 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        response_content_obj에 label, action, action에 따른 필드를 저장합니다.
        action이 "Message"인 경우 messageText를 저장하고,
        action이 "Block"인 경우 blockId를 저장합니다.
        extra가 존재하는 경우 extra를 저장합니다.
        최종적으로 response_content_obj를 반환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 QuickReply 딕셔너리
        """
        self.validate()
        self.response_content_obj = {
            "label": self.label,
            "action": self.action.value,
        }

        self.response_content_obj[QuickReply.action_field_map[
            self.action]] = getattr(self,
                                    QuickReply.action_field_map[self.action])

        if self.extra is not None:
            self.response_content_obj["extra"] = self.extra

        return self.response_content_obj


class QuickReplies(Common):
    """카카오톡 응답 형태 QuickReplies의 객체를 생성하는 클래스

    QuickReplies는 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    QuickReply 객체들의 리스트로 구성됩니다.

    add_quick_reply 메서드를 통해 QuickReply 객체를 추가하고,
    delete_quick_reply 메서드를 통해 QuickReply 객체를 삭제할 수 있습니다.

    from_buttons 메서드를 통해 Buttons 객체를 QuickReplies 객체로 변환할 수 있습니다.

    Args:
        quickReplies (list[QuickReply]): QuickReply 객체들의 리스트, 기본값은 빈 리스트
    """

    def __init__(self, quickReplies: Optional[list[QuickReply]] = None):
        super().__init__()
        if quickReplies is None:
            quickReplies = []
        self.quickReplies: list[QuickReply] = quickReplies
        self.response_content_obj: list = []

    def __add__(self, other: "QuickReplies") -> "QuickReplies":
        """QuickReplies 객체를 합칩니다.

        Args:
            other (QuickReplies): 합칠 QuickReplies 객체

        Returns:
            QuickReplies: 합쳐진 QuickReplies 객체
        """
        validate_type(QuickReplies, other)
        return QuickReplies(self.quickReplies + other.quickReplies)

    def validate(self):
        """QuickReplies 객체의 유효성을 검사합니다.

        quickReplies의 각 요소가 QuickReply 객체인지 확인합니다.

        Raises:
            InvalidTypeError: quickReplies의 각 요소가 QuickReply 객체가 아닌 경우
        """
        for quickReply in self.quickReplies:
            validate_type(QuickReply, quickReply)

    @overload  # type: ignore
    def add_quick_reply(self, quickReply: QuickReply) -> None:  # noqa: F811
        ...

    @overload
    def add_quick_reply(
            self,
            label: str,
            action: str,
            messageText: Optional[str] = None,
            blockId: Optional[str] = None,
            extra: Optional[dict] = None) -> None:
        ...

    def add_quick_reply(self, *args, **kwargs) -> None:
        """QuickReplies에 QuickReply를 추가합니다.

        QuickReply 객체 또는 QuickReply 생성 인자를 받아 QuickReplies에 추가합니다.

        QuickReply 객체를 받은 경우
        Args:
            quickReply (QuickReply): 추가할 QuickReply 객체

        QuickReply 생성 인자를 받은 경우
        Args:
            label (str): QuickReply의 라벨
            action (str): QuickReply의 액션
            messageText (str): QuickReply의 messageText
            blockId (str): QuickReply의 blockId
            extra (dict): QuickReply의 extra

        Raises:
            InvalidTypeError: 받거나 생성한 QuickReply 객체가 QuickReply가 아닌 경우
        """
        if len(args) == 1 and isinstance(args[0], QuickReply):
            quickReply = args[0]
        else:
            quickReply = QuickReply(*args, **kwargs)
        validate_type(QuickReply, quickReply)
        self.quickReplies.append(quickReply)

    def delete_quick_reply(self, quickReply: QuickReply):
        """QuickReplies에서 QuickReply를 삭제합니다.

        Args:
            quickReply (QuickReply): 삭제할 QuickReply 객체
        """
        self.quickReplies.remove(quickReply)

    def render(self) -> list:
        """QuickReplies 객체를 카카오톡 응답 형식에 맞게 리스트로 변환합니다.

        QuickReplies 객체의 각 QuickReply 객체를 render 메서드를 통해 변환하고,
        변환된 QuickReply 객체들을 리스트로 반환합니다.

        Returns:
            list: 카카오톡 응답 형식에 맞게 변환된 QuickReplies 객체의 리스트
        """
        self.validate()
        self.response_content_obj = [
            quickReply.render() for quickReply in self.quickReplies
        ]
        return self.response_content_obj

    def get_list(self, rendering: bool = False) -> list:
        """QuickReplies 객체를 카카오톡 응답 형식에 맞게 리스트로 변환합니다.

        QuickReplies 객체의 각 QuickReply 객체를 render 메서드를 통해 변환하고,
        변환된 QuickReply 객체들을 리스트로 반환합니다.

        Returns:
            list: 카카오톡 응답 형식에 맞게 변환된 QuickReplies 객체의 리스트
        """
        if rendering:
            return self.render()
        return self.response_content_obj

    @classmethod
    def from_buttons(cls, buttons: "Buttons") -> "QuickReplies":
        """Buttons 객체를 QuickReplies 객체로 변환합니다.

        Buttons 객체의 각 Button 객체를 QuickReply 객체로 변환하여 QuickReplies 객체로 반환합니다.

        Args:
            buttons (Buttons): 변환할 Buttons 객체

        Returns:
            QuickReplies: Buttons 객체를 변환한 QuickReplies 객체

        Raises:
            InvalidTypeError: buttons의 각 요소가 Button 객체가 아닌 경우
        """
        quick_replies = []
        for button in buttons:
            assert isinstance(button, Button)
            quick_replies.append(
                QuickReply(
                    label=button.label,
                    action=button.action,
                    messageText=button.messageText,
                    blockId=button.blockId,
                ))
        return cls(quick_replies)


class Button(Common):
    """카카오톡 응답 형태 Button의 객체를 생성하는 클래스

    Button은 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    Buttons 객체의 속성으로 사용됩니다.

    Attributes:
        label (str): 버튼의 텍스트
        action (Action): 버튼의 동작
        webLinkUrl (str): 웹 링크
        messageText (str): 메시지
        phoneNumber (str): 전화번호
        blockId (str): 블록 ID
        extra (dict): 스킬 서버에 추가로 전달할 데이터

    Raises:
        ValueError: text가 문자열이 아닌 경우
    """

    # Button의 action에 따라 필요한 필드를 매핑하는 딕셔너리
    action_field_map = {
        Action.WEBLINK: "webLinkUrl",
        Action.MESSAGE: "messageText",
        Action.PHONE: "phoneNumber",
        Action.BLOCK: "blockId"
    }

    def __init__(
            self,
            label: str,
            action: str | Action,
            webLinkUrl: Optional[str] = None,
            messageText: Optional[str] = None,
            phoneNumber: Optional[str] = None,
            blockId: Optional[str] = None,
            extra: Optional[dict] = None):

        super().__init__()
        self.label = label
        self.action = self.process_action(action)
        self.webLinkUrl = webLinkUrl
        self.messageText = messageText
        self.phoneNumber = phoneNumber
        self.blockId = blockId
        self.extra = extra

    @staticmethod
    def process_action(action: str | Action) -> Action:
        """문자열 또는 Action 열거형 인스턴스를 Action 열거형으로 변환합니다.

        action이 문자열인 경우 대문자로 변환하여 Action 열거형에 있는지 확인합니다.
        Action 열거형에 없는 경우 InvalidActionError를 발생시킵니다.

        Args:
            action (str | Action): Button의 action

        Returns:
            Action: Button의 action을 나타내는 Action 열거형

        Raises:
            InvalidActionError: 유효하지 않은 action 값인 경우
        """
        validate_type(
            (str, Action),
            action,
            disallow_none=True,
            exception_type=InvalidActionError)

        if isinstance(action, str):
            # getattr을 사용하여 안전하게 Action 열거형에 접근
            result = getattr(Action, action.upper(), None)
            if result is None:
                raise InvalidActionError(f"유효하지 않은 action 값: {action}")
            return result

        return action

    def validate(self):
        """Button 객체의 유효성을 검사합니다.

        label이 문자열이 아닌 경우 InvalidTypeError를 발생시킵니다.
        action에 따라 필요한 필드가 존재하는지 확인합니다.

        Raise:
            InvalidTypeError: label이 문자열이 아닌 경우
            InvalidTypeError: action에 따라 필요한 필드가 존재하지 않는 경우
        """
        validate_str(self.label)

        field_to_validate = getattr(self, Button.action_field_map[self.action])
        validate_str(field_to_validate)

    def render(self) -> dict:
        """Button 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        response_content_obj에 label, action, action에 따른 필드를 저장합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Button 딕셔너리
        """
        self.validate()
        self.response_content_obj = {
            "label": self.label,
            "action": self.action.value,
        }

        self.response_content_obj[Button.action_field_map[
            self.action]] = getattr(self, Button.action_field_map[self.action])

        if self.extra is not None:
            self.response_content_obj.update(self.extra)

        return self.response_content_obj


class Buttons(Common):
    """카카오톡 응답 형태 Buttons의 객체를 생성하는 클래스

    Buttons는 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    response_content_obj에 Button 객체들의 리스트로 저장됩니다.
    iter 메서드를 통해 Button 객체들을 순회할 수 있습니다.
    add_button 메서드를 통해 Button 객체를 추가하고,
    delete_button 메서드를 통해 Button 객체를 삭제할 수 있습니다.
    render 메서드를 통해 Buttons 객체를 response 객체에 넣을 수 있는 형태로 변환합니다.
    """

    def __init__(
            self,
            buttons: Optional[list[Button]] = None,
            max_buttons: int = 3):
        super().__init__()
        self._buttons = buttons or []
        self.max_buttons = max_buttons

    def __len__(self):
        """버튼의 개수를 반환합니다.

        Returns:
            int: 버튼의 개수
        """
        return len(self._buttons)

    def __iter__(self):
        """버튼을 순회할 수 있도록 반환합니다.

        Returns:
            iter: 버튼을 순회할 수 있는 이터레이터
        """
        return iter(self._buttons)

    def validate(self):
        """Buttons 객체의 유효성을 검사합니다.

        버튼의 개수가 최대 개수를 초과하는 경우 InvalidTypeError를 발생시킵니다.

        Raises:
            InvalidTypeError: 버튼의 개수가 최대 개수를 초과하는 경우
            InvalidTypeError: 버튼이 Button 객체가 아닌 경우
        """
        if len(self._buttons) > self.max_buttons:
            raise InvalidTypeError(f"버튼은 최대 {self.max_buttons}개까지 가능합니다.")
        if False in [isinstance(button, Button) for button in self._buttons]:
            raise InvalidTypeError("self._buttons는 Button으로 이루어져야 합니다.")

    @overload
    def add_button(self, button: Button) -> None:
        ...

    @overload
    def add_button(
            self,
            label: str,
            action: str | Action,
            webLinkUrl: Optional[str] = None,
            messageText: Optional[str] = None,
            phoneNumber: Optional[str] = None,
            blockId: Optional[str] = None,
            extra: Optional[dict] = None):
        ...

    def add_button(self, *args, **kwargs) -> None:
        """버튼을 추가합니다.

        Button 객체 또는 Button 생성 인자를 받아 버튼 리스트에 추가합니다.

        Button 객체를 받은 경우
        Args:
            button (Button): 추가할 Button 객체

        Button 생성 인자를 받은 경우
        Args:
            label (str): 버튼의 텍스트
            action (str): 버튼의 동작
            web_link_url (str): 웹 링크
            message_text (str): 메시지
            phone_number (str): 전화번호
            block_id (str): 블록 ID
            extra (dict): 스킬 서버에 추가로 전달할 데이터

        Raises:
            InvalidTypeError: 받거나 생성한 Button 객체가 Button이 아닌 경우
        """
        if len(args) == 1 and isinstance(args[0], Button):
            button = args[0]
        elif len(kwargs) == 1 and "button" in kwargs:
            button = kwargs["button"]
        else:
            button = Button(*args, **kwargs)
        validate_type(Button, button, disallow_none=True)
        self._buttons.append(button)

    def delete_button(self, button: Button):
        """버튼을 삭제합니다.

        Args:
            button (Button): 삭제할 버튼 객체

        Raises:
            ValueError: 버튼이 버튼 리스트에 존재하지 않는 경우
        """
        if button not in self._buttons:
            raise ValueError("해당 버튼이 존재하지 않습니다.")
        self._buttons.remove(button)

    def render(self) -> list:
        """Buttons 객체를 카카오톡 응답 형식에 맞게 리스트로 변환합니다.

        버튼의 각 Button 객체를 render 메서드를 통해 변환하고,
        변환된 Button 객체들을 리스트로 반환합니다.

        Returns:
            list: 카카오톡 응답 형식에 맞게 변환된 Button 객체의 리스트
        """
        self.validate()
        return [button.render() for button in self._buttons]


class Link(Common):
    """카카오톡 응답 형태 Link의 객체를 생성하는 클래스

    Link는 버튼이나 썸네일 등에서 사용되는 링크를 나타냅니다.
    Link 객체는 웹, PC, 모바일 링크를 가질 수 있습니다.
    web이 가장 우선적으로 실행되며, web이 없는 경우에 플랫폼에 따라 PC 또는 모바일 링크가 실행됩니다.

    Args:
        web (Optional[str]): 웹 링크
        pc (Optional[str]): PC 링크
        mobile (Optional[str]): 모바일 링크
    """

    def __init__(
            self,
            web: Optional[str] = None,
            pc: Optional[str] = None,
            mobile: Optional[str] = None):
        super().__init__()
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

        response_content_obj에 web, pc, mobile 링크를 저장합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Link 딕셔너리
        """
        self.validate()
        return self.create_dict_with_non_none_values(
            web=self.web,
            pc=self.pc,
            mobile=self.mobile,
        )


class Thumbnail(Common):
    """카카오톡 응답 형태 Thumbnail의 객체를 생성하는 클래스

    Thumbnail은 썸네일 이미지를 나타냅니다.
    썸네일 이미지는 이미지 URL을 가지며, 링크를 가질 수 있습니다.
    fixedRatio는 이미지의 비율을 고정할지 여부를 나타냅니다.

    Args:
        image_url (str): 썸네일 이미지 URL
        link (Link): 썸네일 이미지 클릭 시 이동할 링크, 기본값은 None
        fixed_ratio (bool): 이미지의 비율을 고정할지 여부, 기본값은 False
    """

    def __init__(
            self,
            image_url: str,
            link: Optional[Link] = None,
            fixed_ratio: bool = False):
        super().__init__()
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

        response_content_obj에 image_url, fixed_ratio, link를 저장합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Thumbnail 딕셔너리
        """
        self.validate()
        self.response_content_obj = {
            "imageUrl": self.image_url,
            "fixedRatio": self.fixed_ratio,
        }
        self.create_dict_with_non_none_values(
            base=self.response_content_obj,
            link=self.link.render() if self.link is not None else None)
        return self.response_content_obj


class Thumbnails(Common):
    """카카오톡 응답 형태 Thumbnails의 객체를 생성하는 클래스

    Thumbnails는 썸네일 이미지들의 리스트를 나타냅니다.
    CommerceCard 객체의 속성으로 사용됩니다.
    현재 카카오톡 규정에 따라 1개의 썸네일 이미지만 사용할 수 있습니다.

    Args:
        thumbnails (list[Thumbnail]): 썸네일 이미지들의 리스트, 기본값은 빈 리스트
        max_thumbnails (int): 썸네일 이미지의 최대 개수, 기본값은 1
    """

    def __init__(self, thumbnails: list[Thumbnail], max_thumbnails: int = 1):
        super().__init__()
        self._thubnails = thumbnails
        self.max_thumbnails = max_thumbnails

    def validate(self):
        """Thumbnails 객체의 유효성을 검사합니다.

        썸네일 이미지의 개수가 최대 개수를 초과하는 경우 InvalidTypeError를 발생시킵니다.
        썸네일 이미지의 각 요소가 Thumbnail 객체인지 확인합니다.

        Raises:
            InvalidTypeError: 썸네일 이미지의 개수가 최대 개수를 초과하는 경우
        """
        if len(self._thubnails) > self.max_thumbnails:
            raise InvalidTypeError(f"버튼은 최대 {self.max_thumbnails}개까지 가능합니다.")
        for thumbnail in self._thubnails:
            validate_type(Thumbnail, thumbnail)

    def add_button(self, thumbnail: Thumbnail):
        """Thumnail 버튼을 추가합니다.

        Args:
            thumbnail (Thumbnail): 추가할 Thumbnail 객체

        Raise:
            ValueError: 이미 최대 버튼 개수에 도달한 경우
            InvalidTypeError: 인자가 Thumbnail 객체가 아닌 경우
        """

        if len(self._thubnails) > self.max_thumbnails:
            raise ValueError("버튼은 최대 3개까지 가능합니다.")

        validate_type(thumbnail, Thumbnail)
        self._thubnails.append(thumbnail)

    def delete_button(self, thumbnail: Thumbnail):
        """Thumnail 버튼을 삭제합니다.

        Args:
            thumbnail (Thumbnail): 삭제할 Thumbnail 객체

        Raise:
            ValueError: 버튼이 존재하지 않는 경우
        """
        if thumbnail not in self._thubnails:
            raise ValueError("해당 버튼이 존재하지 않습니다.")
        self._thubnails.remove(thumbnail)

    def render(self) -> list:
        """Thumbnails 객체를 카카오톡 응답 형식에 맞게 리스트로 변환합니다.

        썸네일 이미지의 각 Thumbnail 객체를 render 메서드를 통해 변환하고,
        변환된 Thumbnail 객체들을 리스트로 반환합니다.

        Returns:
            list: 카카오톡 응답 형식에 맞게 변환된 Thumbnail 객체의 리스트
        """
        self.validate()
        return [thumbnail.render() for thumbnail in self._thubnails]


class Profile(Common):
    """카카오톡 응답 형태 Profile의 객체를 생성하는 클래스

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
        return self.create_dict_with_non_none_values(
            nickname=self.nickname,
            imageUrl=self.image_url)


class ListItem(Common):
    """카카오톡 응답 형태 ListItem의 객체를 생성하는 클래스

    ListItem은 리스트 형태의 정보를 나타냅니다.
    ListItem은 title, description, imageUrl, link, action, block_id,
    message_text, extra를 가질 수 있습니다.
    ListCard 객체의 속성인 ListItems의 속성으로 사용됩니다.

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
            InvalidTypeError: title이 문자열이 아닌 경우
            InvalidTypeError: description이 문자열이 아닌 경우
            InvalidTypeError: image_url이 문자열이 아닌 경우
            InvalidTypeError: link가 Link 객체가 아닌 경우
        """
        validate_str(
            self.title, self.description, self.image_url,
            self.block_id, self.message_text)
        validate_type(Link, self.link)

    def render(self):
        """ListItem 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 ListItem 딕셔너리
        """
        self.validate()
        self.response_content_obj = {
            "title": self.title,
            "description": self.description,
            "imageUrl": self.image_url,
        }

        self.create_dict_with_non_none_values(
            base=self.response_content_obj,
            link=self.link.render() if self.link is not None else None,
            action=self.action,
            blockId=self.block_id,
            messageText=self.message_text,
        )
        return self.response_content_obj


class ListItems(Common):
    """카카오톡 응답 형태 ListItems의 객체를 생성하는 클래스

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

    def add_list_item(self, list_item: ListItem):
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

    def delete_list_item(self, list_item: ListItem):
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


if __name__ == "__main__":
    testbutton = Button(
        label="구경하기",
        action="webLink",
        webLinkUrl="https://sio2.pe.kr/login",
        messageText=None)
    print(testbutton.render())