import json
from typing import Optional, Union, overload

from .components.base import ParentComponent

from .interactiron import ActionEnum, Interaction
from ..base import BaseModel
from ..context import Context
from ..validation import validate_str, validate_type
from ..base import SkillTemplate


class QuickReply(SkillTemplate, Interaction):
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
    available_action_enums: list[ActionEnum] = [
        ActionEnum.MESSAGE, ActionEnum.BLOCK]

    def __init__(
            self,
            label: str,
            action: str | ActionEnum = "Message",
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
        Interaction.__init__(self, action=action, extra=extra)
        self.label = label
        self.message_text = message_text
        self.block_id = block_id

    def validate(self):
        """QuickReply 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: label이 문자열이 아닌 경우
            InvalidTypeError: message_text가 문자열이 아닌 경우
            InvalidTypeError: block_id가 문자열이 아닌 경우
        """
        validate_str(self.label, self.message_text, self.block_id)
        Interaction.validate(self)

    def render(self) -> dict:
        """QuickReply 객체를 카카오톡 응답 형식에 맞게 딕셔너리로 변환합니다.

        ex) {
            "label": "바로가기 1",
            "action": "message",
            "messageText": "바로가기 1 클릭"
        }

        Returns:
            dict: 렌더링된 QuickReply
        """
        self.validate()
        response = {
            "label": self.label,
        }
        response.update(Interaction.render(self))
        return response


class KakaoResponse(BaseModel):
    """복수개의 ParentComponent 반환하기 위한 응답 객체

    여러 ParentComponent 객체를 카카오톡 출력 요소 형식에 맞게 변환합니다.

    Attributes:
        component_list (list[ParentComponent]): ParentComponent 객체들을 담는 리스트
        quick_replies (list[QuickReply]): QuickReply 객체들을 담는 리스트
        response_content_obj (dict): 카카오톡 출력 요소의 객체
        max_component_count (int): 포함할 수 있는 ParentComponent 객체의 최대 개수
        max_quick_reply_count (int): 포함할 수 있는 QuickReply 객체의 최대 개수

    example:
        >>> from kakao import KakaoResponse, SimpleText
        >>> response = KakaoResponse()
        >>> response += SimpleTextComponent("안녕하세요!")
        >>> response.add_component(SimpleText("반가워요!"))
        >>> response += QuickReply("안녕", "message", "안녕하세요!")
        >>> response.get_dict()
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "안녕하세요!"
                        }
                    },
                    {
                        "simpleText": {
                            "text": "반가워요!"
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "label": "안녕",
                        "action": "message",
                        "messageText": "안녕하세요!"
                    }
                ]
            }
        }
    """

    def __init__(
            self,
            component_list: Optional[
                list[ParentComponent] | ParentComponent
            ] = None,
            quick_replies: Optional[list[QuickReply] | QuickReply] = None,
            contexts: Optional[list[Context]] = None,
            data: Optional[dict[str, str]] = None):
        """KakaoResponse 객체를 생성합니다.

        Args:
            component_list (list[ParentComponent], optional): ParentComponent
                                                        객체들을 담는 리스트 (기본값: None)
            quick_replies (list[QuickReply] , optional): QuickReply
                                                        객체들을 담는 리스트 (기본값: None)
            contexts (list[dict], optional): Context 객체들을 담는 리스트 (기본값: None)
            data (dict, optional): 추가적인 데이터 (기본값: None)
        """
        if component_list is None:
            component_list = []
        elif isinstance(component_list, ParentComponent):
            component_list = [component_list]
        self.component_list = component_list

        if quick_replies is None:
            quick_replies = []
        elif isinstance(quick_replies, QuickReply):
            quick_replies = [quick_replies]
        self.quick_replies = quick_replies

        if contexts is None:
            contexts = []
        self.contexts = contexts
        self.data = data

        self.max_component_count = 3
        self.max_quick_reply_count = 10
        self.response_content_obj: dict = {}

    @property
    def is_empty(self) -> bool:
        """컴포넌트 리스트가 비어있는지 여부를 반환합니다.

        Returns:
            bool: 컴포넌트 리스트가 비어있으면 True, 아니면 False
        """
        return bool(self.component_list)

    def validate(self):
        """객체를 카카오톡 응답 규칙에 알맞은지 검증합니다. (super 참고)

        component_list에 포함된 ParentComponent 객체들을 검증합니다.
        quick_replies에 포함된 QuickReply 객체들을 검증합니다.
        contexts에 포함된 Context 객체들을 검증합니다.
        data가 dict 타입인지 검증합니다.


        Raises:
            ValueError: 최대 ParentComponent 개수를 초과하는 경우
            ValueError: 최대 QuickReply 개수를 초과하는 경우
            InvalidTypeError: data가 dict 타입이 아닌 경우
        """

        # component_list의 길이 검증
        if len(self.component_list) > self.max_component_count:
            raise ValueError((
                f"최대 {self.max_component_count}개의 "
                "ParentComponent을 포함할 수 있습니다."))

        # component_list에 포함된 ParentComponent 객체들을 검증
        for component in self.component_list:
            assert isinstance(component, ParentComponent)
            component.validate()

        # quick_replys의 길이 검증
        if len(self.quick_replies) > self.max_quick_reply_count:
            raise ValueError(
                f"최대 {self.max_quick_reply_count}개의 QuickReply를 포함할 수 있습니다.")

        # quick_replies에 포함된 QuickReplies 객체를 검증
        for quick_reply in self.quick_replies:
            assert isinstance(quick_reply, QuickReply)
            quick_reply.validate()

        # contexts에 포함된 Context 객체를 검증
        for context in self.contexts:
            assert isinstance(context, Context)
            context.validate()

        validate_type(dict, self.data)

    def render(self) -> dict:
        """객체를 카카오톡 출력 요소 형식에 맞게 변환합니다. (super 참고)

        component_list의 render 메서드를 호출하여 카카오톡 출력 요소 형식에 맞게 변환합니다.
        이를 response_content_obj에 저장합니다.

        Returns:
            dict: 카카오톡 출력 요소의 객체
        """
        self.validate()

        template = {}

        # component_list가 있는 경우 추가
        if self.component_list:
            # component_list의 각 ParentComponent 객체를 렌더링하여 outputs에 추가
            template['outputs'] = [
                {component.__class__.name: component.render()}
                for component in self.component_list
            ]

        # quick_replies가 있는 경우 추가
        if self.quick_replies:
            template['quickReplies'] = [quick_reply.render()
                                        for quick_reply in self.quick_replies]

        # 최종 출력 요소 구성
        self.response_content_obj = {
            'version': '2.0',
            'template': template if template else None,
            'context': (
                [context.render() for context in self.contexts]
                if self.contexts else None
            ),
            'data': self.data
        }
        self.response_content_obj = self.remove_none_item(
            self.response_content_obj)

        return self.response_content_obj

    def add_component(self, component: "ParentComponent") -> "KakaoResponse":
        """ParentComponent 추가합니다.

        반환할 ParentComponent 객체를 component_list에 추가합니다.

        Args:
            component (ParentComponent): 추가할 ParentComponent 객체

        Returns:
            KakaoResponse: ParentComponent 객체가 추가된 KakaoResponse 객체
        """

        # 추가할 ParentComponent Carousel인 경우
        # Carousel에 포함된 ParentComponent solo_mode를 False로 설정
        # Carousel이 비어있는 경우 추가하지 않음
        self.component_list.append(component)
        return self

    def get_dict(self, rendering: bool = True) -> dict:
        """카카오톡 출력 요소 형식에 알맞은 dict를 반환합니다.

        response_content_obj를 반환합니다.
        rendering이 True인 경우, render 메서드를 호출하여
        response_content_obj를 갱신한 후 반환합니다.

        Args:
            rendering (bool): render 메서드를 호출할지 여부. 기본값은 True입니다.
                        False로 설정할 경우, render 메서드를 호출하지 않습니다.
                        render가 중복 호출되는 것을 방지할 때 사용합니다.

        Returns:
            dict: 카카오톡 출력 요소의 딕셔너리
        """
        if rendering:
            self.render()
        return self.response_content_obj

    def get_json(self, ensure_ascii: bool = True, **kwargs) -> str:
        """카카오톡 출력 요소 형식에 알맞은 JSON 문자열을 반환합니다.

        get_dict() 메서드를 호출하여 dict를 반환한 후,
        json.dumps() 함수를 사용하여 JSON 문자열로 변환합니다.

        Args:
            ensure_ascii (bool): json.dumps() 함수에 전달되는 인자입니다. 기본값은 True입니다.
            **kwargs: json.dumps() 함수에 전달되는 추가적인 인자들입니다.
        """
        return json.dumps(
            self.get_dict(), ensure_ascii=ensure_ascii, **kwargs
        )

    @overload
    def add_quick_reply(self, quick_reply: QuickReply) -> "KakaoResponse":
        """quick_replies에 QuickReply를 객체로 추가합니다.

        Args:
            quick_reply (QuickReply): 추가할 QuickReply 객체
        """

    @overload
    def add_quick_reply(
            self,
            label: str,
            action: str,
            message_text: Optional[str] = None,
            block_id: Optional[str] = None,
            extra: Optional[dict] = None) -> "KakaoResponse":
        """quick_replies에 QuickReply 생성 인자로 QuickReply 객체를 생성하여 추가합니다.

        Args:
            label (str): 사용자에게 노출될 바로가기 응답의 표시
            action (str): 바로가기 응답의 기능 ‘message’ 혹은 ‘block’
            message_text (str): 사용자 측으로 노출될 발화(action이 'message'인 경우)
            block_id (str): 연결될 블록의 id(action이 'block'인 경우)
            extra (dict): 블록을 호출 시 추가적으로 제공하는 정보
        """

    def add_quick_reply(self, *args, **kwargs) -> "KakaoResponse":
        """quick_replies에 QuickReply를 추가합니다.

        Args:
            *args: QuickReply 객체 또는 QuickReply 생성 인자
            **kwargs: QuickReply 객체 또는 QuickReply 생성 인자
        """
        if len(args) == 1 and isinstance(args[0], QuickReply):
            quick_reply = args[0]
        elif len(args) == 0 and "quick_reply" in kwargs:
            quick_reply = kwargs["quick_reply"]
        else:
            quick_reply = QuickReply(*args, **kwargs)
        self.quick_replies.append(quick_reply)

        return self

    @overload
    def add_context(
            self,
            name: str,
            lifespan: int,
            ttl: Optional[int] = None,
            params: Optional[dict] = None) -> "KakaoResponse":
        """Context 생성 인자로 Context 객체를 생성하여 contexts에 추가합니다.

        Args:
            name (str): 컨텍스트의 이름
            lifespan (int): 컨텍스트의 남은 횟수
            ttl (int): 컨텍스트가 유지되는 시간
            params (dict, optional): 컨텍스트의 추가 정보
        """

    @overload
    def add_context(self, context: Context) -> "KakaoResponse":
        """Context를 추가합니다.

        Args:
            context (Context): 추가할 Context 객체
        """

    def add_context(self, *args, **kwargs) -> "KakaoResponse":
        """Context를 contexts에 추가합니다.

        Args:
            *args: Context 객체 또는 Context 생성 인자
            **kwargs: Context 객체 또는 Context 생성 인자
        """
        if len(args) == 1 and isinstance(args[0], Context):
            context = args[0]
        elif len(args) == 0 and "context" in kwargs:
            context = kwargs["context"]
        else:
            context = Context(*args, **kwargs)

        self.contexts.append(context)
        return self

    @overload
    def __add__(self, other: QuickReply) -> "KakaoResponse": ...

    @overload
    def __add__(self, other: ParentComponent) -> "KakaoResponse": ...

    @overload
    def __add__(self, other: "KakaoResponse") -> "KakaoResponse": ...

    @overload
    def __add__(self, other: "Context") -> "KakaoResponse": ...

    def __add__(
            self,
            other: Union[QuickReply, ParentComponent, "KakaoResponse", Context]
    ) -> "KakaoResponse":
        """합 연산자 정의

        QuickReply, ParentComponent, KakaoResponse 객체를 합할 수 있습니다.
        QuickReply 객체를 추가할 경우, 현재 객체의 quick_replies에 해당 객체를 추가합니다.
        ParentComponent 객체를 추가할 경우, 현재 객체의 component_list에 해당 객체를 추가합니다.
        KakaoResponse 객체를 추가할 경우, 두 객체의 component_list를 합한 후,
                        두 객체의 quick_replies를 합합니다.
        Context 객체를 추가할 경우, 현재 객체의 contexts에 해당 객체를 추가합니다.

        Args:
            other (QuickReply): 추가할 QuickReply 객체
            other (ParentComponent): 추가할 ParentComponent 객체
            other (component_list): 추가할 component_list 객체
            other (KakaoResponse): 추가할 KakaoResponse 객체

        Returns:
            KakaoResponse: 객체가 추가된 KakaoResponse 객체

        Examples:
        >>> response = KakaoResponse()
        >>> response += SimpleTextComponent("안녕하세요!")
        >>> response.add_component(SimpleText("반가워요!"))
        >>> response += QuickReply("안녕", "message", "안녕하세요!")
        >>> response.get_dict()
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "안녕하세요!"
                        }
                    },
                    {
                        "simpleText": {
                            "text": "반가워요!"
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "label": "안녕",
                        "action": "message",
                        "messageText": "안녕하세요!"
                    }
                ]
            }
        }
        """

        if isinstance(other, QuickReply):
            self.add_quick_reply(other)

        if isinstance(other, ParentComponent):
            self.add_component(other)

        if isinstance(other, KakaoResponse):
            self.component_list += other.component_list

            # 퀵리플라이가 있는 경우 합쳐줌
            if other.quick_replies:
                self.quick_replies += other.quick_replies

        if isinstance(other, Context):
            self.add_context(other)
        return self
