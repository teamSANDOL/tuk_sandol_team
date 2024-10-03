"""카카오톡 출력 요소의 객체를 생성하는 클래스들을 정의한 모듈입니다.

주로 스킬 응답들이 공통으로 사용되는 속성을 객체화 하는 추상 클래스입니다.
Common이 아닌 다른 SkillTemplate의 출력 요소의 구성 요소로 사용됩니다.
ListItem은 ListCard의 items에 들어가는 Item을 나타내는 클래스로써
ListCard 에서만 사용됩니다.

classes:
    Common: 카카오톡 출력 요소의 공통 속성 객체를 의미하는 추상 클래스입니다.
    Action: 카카오톡 출력 요소의 버튼의 동작을 나타내는 열거형 클래스입니다.
    QuickReply: 카카오톡 출력 요소 QuickReply의 객체를 생성하는 클래스입니다.
    Link: 카카오톡 출력 요소 Link의 객체를 생성하는 클래스입니다.
    Thumbnail: 카카오톡 출력 요소 Thumbnail의 객체를 생성하는 클래스입니다.
    Profile: 카카오톡 출력 요소 Profile의 객체를 생성하는 클래스입니다.
    Button: 카카오톡 출력 요소 Button의 객체를 생성하는 클래스입니다.
    ListItem: 카카오톡 출력 요소 ListCard의 items에 들어가는 Item을 나타내는 클래스입니다.
"""

from abc import ABCMeta
from typing import Optional


from ...customerror import InvalidLinkError
from ...validation import validate_str, validate_type
from ..interactiron import ActionEnum, Interaction
from ..base import ParentComponent

__all__ = [
    "Link",
    "Thumbnail",
    "Profile",
    "ListItem",
    "Button",
]


class Common(ParentComponent, metaclass=ABCMeta):
    """스킬 응답들이 공통으로 사용되는 속성을 객체화 하는 추상 클래스입니다.

    명시적으로 스킬 응답의 공통으로 사용되는 속성을 객체화 하기 위해 사용됩니다.
    (ex. Thumbnail, Button 등)

    Common이 아닌 다른 SkillTemplate의 출력 요소의 구성 요소로 사용됩니다.
    (ex. Thumbnail은 BasicCard, CommerceCard의 속성으로 사용됩니다.)
    """


class Link(Common):
    """카카오톡 출력 요소 Link의 객체를 생성하는 클래스

    Link는 버튼이나 썸네일 등에서 사용되는 링크를 나타냅니다.
    Link 객체는 웹, PC, 모바일 링크를 가질 수 있습니다.
    web이 가장 우선적으로 실행되며, web이 없는 경우에 플랫폼에 따라 PC 또는 모바일 링크가 실행됩니다.

    ListItem, ItemThumbnail, Thumbnail, Button의 속성으로 사용됩니다.

    Args:
        web (Optional[str]): 웹 링크
        pc (Optional[str]): PC 링크
        mobile (Optional[str]): 모바일 링크

    Examples:
        >>> link = Link(web="https://www.example.com")
        >>> link.render()
        {'web': 'https://www.example.com'}
    """

    def __init__(
            self,
            web: Optional[str] = None,
            pc: Optional[str] = None,
            mobile: Optional[str] = None):
        """Link 객체의 생성자 메서드입니다.

        Args:
            web (Optional[str], optional): 웹 링크. Defaults to None.
            pc (Optional[str], optional): PC 링크. Defaults to None.
            mobile (Optional[str], optional): 모바일 링크. Defaults to None.
        """
        self.web = web
        self.pc = pc
        self.mobile = mobile

    def validate(self):
        """Link 객체의 유효성을 검사합니다.

        Link는 최소 하나의 링크를 가져야 합니다.
        self.web, self.pc, self.mobile이 모두 None인 경우 InvalidLinkError를 발생시킵니다.

        Raises:
            InvalidLinkError: 링크가 하나도 없는 경우
        """
        if self.web is None and self.pc is None and self.mobile is None:
            raise InvalidLinkError("Link는 최소 하나의 링크를 가져야 합니다.")
        validate_str(self.web, self.pc, self.mobile)

    def render(self) -> dict:
        """Link 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        response에 web, pc, mobile 링크를 저장합니다.
        이후 None인 링크는 제거후 반환합니다.

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

    Thumbnail은 썸네일 이미지를 나타냅니다.
    썸네일 이미지는 이미지 URL을 가지며, 링크를 가질 수 있습니다.
    fixedRatio는 이미지의 비율을 고정할지 여부를 나타냅니다.

    BasicCard, CommerceCard 객체의 속성으로 사용됩니다.

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
        이후 None인 속성은 제거후 반환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Thumbnail 딕셔너리
        """
        self.validate()
        response = {
            "imageUrl": self.image_url,
            "fixedRatio": self.fixed_ratio if self.fixed_ratio else None,
            "link": self.link.render() if self.link is not None else None,
        }

        return self.remove_none_item(response)


class Profile(Common):
    """카카오톡 출력 요소 Profile의 객체를 생성하는 클래스

    Profile은 사용자의 프로필 정보를 나타냅니다.
    이미지 URL은 선택적으로 사용할 수 있습니다.
    이미지 사이즈는 180px X 180px이 권장됩니다.

    CommerceCard, ImageCard 객체의 속성으로 사용됩니다.

    Attributes:
        nickname (str): 사용자의 닉네임
        image_url (Optional[str]): 사용자의 프로필 이미지 URL, 기본값은 None
    """

    def __init__(self, nickname: str, image_url: Optional[str] = None):
        """Profile 클래스의 생성자 메서드입니다.

        Args:
            nickname (str): 사용자의 닉네임
            image_url (Optional[str]): 사용자의 프로필 이미지 URL, 기본값은 None
        """
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

        nickname과 image_url을 response에 저장합니다.
        이후 None인 속성은 제거후 반환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Profile 딕셔너리
        """
        response = {
            "nickname": self.nickname,
            "imageUrl": self.image_url,
        }
        return self.remove_none_item(response)


class Button(Interaction, Common):
    """카카오톡 출력 요소 Button의 객체를 생성하는 클래스

    Button은 사용자가 챗봇에게 빠르게 응답할 수 있도록 도와주는 버튼입니다.
    TextCardComponent, BasicCardComponent, CommerceCardComponent,
    ListCardComponent, ItemCardComponent 객체의 속성으로 사용됩니다.


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

    Examples:
        >>> button = Button(
        ...     label="버튼 1",
        ...     action="message",
        ...     message_text="버튼 1 클릭"
        ... )
        >>> button.render()
        {'label': '버튼 1', 'action': 'message', 'messageText': '버튼 1 클릭'}
    """
    available_action_enums: list[ActionEnum] = [
        action for action in ActionEnum]

    def __init__(
            self,
            label: str,
            action: str | ActionEnum,
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

        assert action is not None, "action은 str 또는 ActionEnum이어야 합니다."
        Interaction.__init__(self, action, extra)
        self.label = label
        self.web_link_url = web_link_url
        self.message_text = message_text
        self.phone_number = phone_number
        self.block_id = block_id

    def validate(self):
        """Button 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: label이 문자열이 아닌 경우
            InvalidTypeError: web_link_url이 문자열이 아닌 경우
            InvalidTypeError: message_text가 문자열이 아닌 경우
            InvalidTypeError: phone_number가 문자열이 아닌 경우
            InvalidTypeError: block_id가 문자열이 아닌 경우
        """

        assert self.action in self.available_action_enums, \
            f"action은 {self.available_action_enums} 중 하나여야 합니다."
        validate_str(
            self.label,
            self.web_link_url,
            self.message_text,
            self.phone_number,
            self.block_id)
        super().validate()

    def render(self) -> dict:
        """Button 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        ex) {
            "label": "버튼 1",
            "action": "message",
            "messageText": "버튼 1 클릭"
        }

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 Button 딕셔너리
        """
        self.validate()
        response = {
            "label": self.label,
        }
        response.update(Interaction.render(self))
        return response


class ListItem(Common, Interaction):
    """카카오톡 출력 요소 ListCard의 items에 들어가는 Item을 나타내는 클래스

    ListItem은 리스트 형태의 정보를 나타냅니다.
    ListItem은 title, description, imageUrl, link, action, block_id,
    message_text, extra를 가질 수 있습니다.

    ListCard 객체의 속성으로 사용됩니다.

    Class Attributes:
        available_action_enums (list[ActionEnum]): 사용 가능한 Action 열거형의 리스트

    Attributes:
        title (str): header에 들어가는 경우, listCard의 제목, items에 들어가는 경우, 해당 항목의 제목
        description (str, optional): items에 들어가는 경우, 해당 항목의 설명
        image_url (str, optional): items에 들어가는 경우, 해당 항목의 우측 안내 사진
        link (Link, optional): 리스트 아이템 클릭 시 동작할 링크
        action (str | Action, optional): 리스트 아이템 클릭시 수행될 작업(block 또는 message)
        block_id (str, optional): action이 block인 경우 block_id를 갖는 블록을 호출
        message_text (str, optional): action이 message인 경우 리스트 아이템 클릭 시 전달할 메시지
        extra (dict, optional): 블록 호출시, 스킬 서버에 추가적으로 제공하는 정보
    """
    available_action_enums = [ActionEnum.BLOCK, ActionEnum.MESSAGE]

    def __init__(
            self,
            title: str,
            description: Optional[str] = None,
            image_url: Optional[str] = None,
            link: Optional[Link] = None,
            action: Optional[str | ActionEnum] = None,
            block_id: Optional[str] = None,
            message_text: Optional[str] = None,
            extra: Optional[dict] = None):
        """ListItem 클래스의 생성자 메서드입니다.

        Args:
            title (str): header이면 listCard, items이면 해당 항목의 제목
            description (str, optional): items에 들어가는 경우, 해당 항목의 설명
            image_url (str, optional): items에 들어가는 경우, 해당 항목의 우측 안내 사진
            link (Link, optional): 리스트 아이템 클릭 시 동작할 링크
            action (str | Action, optional): 아이템 클릭시 수행될 작업(block 또는 message)
            block_id (str, optional): action이 block인 경우 block_id를 갖는 블록을 호출
            message_text (str, optional): message인 경우 리스트 아이템 클릭 시 전달할 메시지
            extra (dict, optional): 블록 호출시, 스킬 서버에 추가적으로 제공하는 정보
        """
        if action is not None:
            Interaction.__init__(self, action=action, extra=extra)
        else:
            self.action = None

        self.title = title
        self.description = description
        self.image_url = image_url
        self.link = link
        self.block_id = block_id
        self.message_text = message_text

    def validate(self):
        """ListItem 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: title이 문자열이 아니거나 None인 경우
            InvalidTypeError: description이 문자열이 아닌 경우
            InvalidTypeError: image_url이 문자열이 아닌 경우
            InvalidTypeError: link가 Link 객체가 아닌 경우
        """
        if self.action:
            Interaction.validate(self)
        validate_str(self.title, disallow_none=True)
        validate_str(self.description, self.image_url)
        validate_type(Link, self.link)

    def render(self):
        """ListItem 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        title, description, imageUrl, link, action,
        block_id, message_text, extra를 response에 저장합니다.
        만약 action이 존재할 경우 Interaction.render()를 통해 action을 추가합니다.
        이후 None인 속성은 제거후 반환합니다.

        Returns:
            dict: 카카오톡 응답 형식에 맞게 변환된 ListItem 딕셔너리
        """
        self.validate()
        response = {
            "title": self.title,
            "description": self.description,
            "imageUrl": self.image_url,
            "link": self.link.render() if self.link else None,
        }
        if self.action:
            action_response = Interaction.render(self)
            response.update(action_response)
        return self.remove_none_item(response)


if __name__ == "__main__":
    testbutton = Button(
        label="구경하기",
        action="webLink",
        web_link_url="https://sio2.pe.kr/login",
        message_text=None)
    print(testbutton.render())
