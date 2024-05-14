from abc import ABCMeta, abstractmethod
from typing import Optional, overload


from .common import Button
from ...base import SkillTemplate
from ..interactiron import ActionEnum
from ...validation import validate_type


class ParentComponent(SkillTemplate, metaclass=ABCMeta):
    """카카오톡 출력 요소의 객체를 생성하는 추상 클래스

    SkillTemplate 참고

    Abstract Methods:
        render: 구체적인 응답 내용을 반환합니다.
            딕셔너리로 카카오톡 출력 요소의 반환 형식에 맞게 반환합니다.
            remove_none_item 메서드를 사용하여 None인 값은 제외 후 반환합니다.

    Methods:
        validate: 객체를 카카오톡 응답 규칙에 알맞은지 검증합니다.
            super().validate()를 호출하여 name 속성이 구현되어 있는지 검증하고,
            각 클래스의 속성이 카카오톡 응답 규칙에 맞는지 검증합니다.

    Raises:
        NotImplementedError: render 또는 validate 메서드가 구현되지 않았을 때

    Examples:
        >>> class TextCard(ParentComponent):
        ...     name = "textCard"   # 응답 객체의 템플릿 이름
        >>> print(TextCard.name)
        ... "textCard"
    """
    name = "ParentComponent"  # 응답 객체의 템플릿 이름 (상속 클래스에서 오버라이딩 필요/ Carousel이 사용)

    def validate(self):
        """객체를 카카오톡 응답 규칙에 알맞은지 검증합니다.

        하위 클래스에서 이 메서드를 오버라이딩하여 구현해야 합니다.
        하위 클래스에서 super().validate()를 호출하여
        클래스 속성인 name이 구현되어 있는지 검증하고,
        quick_replies 객체의 검증을 수행합니다.

        검증에 실패할 경우 예외를 발생시킵니다.
        검증 내용은 카카오톡 응답 규칙에 따라 구현되어야 합니다.

        (예) 객체 속성의 타입이 올바른지, 값이 올바른지,
            응답의 길이가 적절한지 등을 검증합니다.
        """
        if "Parent" in self.__class__.name:
            raise NotImplementedError("name 속성을 구현해야 합니다.")


class ParentCardComponent(ParentComponent):
    """Component 출력 요소중 Card 종류의 부모 클래스입니다.

    Card 출력 요소는 TextCardComponent, BasicCardComponent,
    CommerceCardComponent, ListCardComponent, ItemCardComponent가 있습니다.
    이 클래스는 Card 출력 요소의 공통 속성과 메서드를 정의합니다.
    주로 Button 객체를 조작하는 메서드를 제공합니다.

    Attributes:
        buttons (list[Button], optional): 버튼 객체입니다.
    """

    def __init__(self, buttons: Optional[list[Button]] = None):
        """ParentCard 객체를 생성합니다.

        Args:
            buttons (Optional[Buttons], optional): 버튼 객체. Defaults to None.
        """
        if buttons is None:
            buttons = []
        self.buttons = buttons

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        Raises:
            InvalidTypeError: 받거나 생성한 Button 객체가 Button이 아닌 경우
        """
        super().validate()
        if self.buttons:
            for button in self.buttons:
                validate_type(Button, button)

    @overload
    def add_button(self, button: Button) -> "ParentCardComponent":
        """버튼을 객체로 입력받아 추가합니다.

        Args:
            button (Button): 추가할 Button 객체

        Returns:
            ParentCardComponent: Button이 추가된 객체
        """

    @overload
    def add_button(
            self,
            label: str,
            action: str | ActionEnum,
            web_link_url: Optional[str] = None,
            message_text: Optional[str] = None,
            phone_number: Optional[str] = None,
            block_id: Optional[str] = None,
            extra: Optional[dict] = None) -> "ParentCardComponent":
        """버튼 생성 인자로 버튼을 추가합니다.

        버튼 생성 인자를 받아 Button 객체를 생성하여 버튼 리스트에 추가합니다.

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

        Returns:
            ParentCard: Button이 추가된 객체
        """

    def add_button(self, *args, **kwargs) -> "ParentCardComponent":
        """버튼을 추가합니다.

        Button 객체 또는 Button 생성 인자를 받아 버튼 리스트에 추가합니다.

        Args:
            *args: Button 생성 인자
            **kwargs: Button 생성 인자

        Returns:
            ParentCard: Button이 추가된 객체

        Raises:
            InvalidTypeError: 받거나 생성한 Button 객체가 Button이 아닌 경우
        """
        if len(args) == 1 and isinstance(args[0], Button):
            self.buttons.append(args[0])
        elif len(args) == 0 and "button" in kwargs:
            self.buttons.append(kwargs["button"])
        else:
            button = Button(*args, **kwargs)
            self.buttons.append(button)
        return self

    def remove_button(self, button: Button):
        """버튼을 제거합니다.

        Button 객체를 받아 버튼 리스트에서 제거합니다.

        Parameters:
            button: 제거할 버튼 객체
        """
        self.buttons.remove(button)

    @abstractmethod
    def render(self): ...
