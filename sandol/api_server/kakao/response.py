import json
from abc import abstractmethod
from typing import Any, Optional, Union, overload

from .common import QuickReplies, QuickReply
from .base import BaseModel


class BaseResponse(BaseModel):
    """카카오톡 응답 객체의 기본 클래스

    카카오톡 응답 객체의 퀵리플라이를 처리하는 메서드를 제공합니다.

    Args:
        quick_replies (QuickReplies): 퀵리플라이 객체

    Attributes:
        quick_replies (QuickReplies): 퀵리플라이 객체
        response_content_obj (dict): 카카오톡 응답 형태의 객체
    """

    def __init__(
            self,
            quick_replies: Optional[QuickReplies] = None):
        self.quick_replies = quick_replies
        self.response_content_obj: dict = {}

    def validate(self):
        """
        객체를 카카오톡 응답 규칙에 알맞은지 검증합니다.
        검증에 실패할 경우 예외를 발생시킵니다.

        검증 내용은 카카오톡 응답 규칙에 따라 구현되어야 합니다.

        (예) 객체 속성의 타입이 올바른지, 값이 올바른지,
            응답의 길이가 적절한지 등을 검증합니다.
        """

        if self.quick_replies:
            self.quick_replies.validate()

    def create_common_response(
            self,
            content: Optional[dict | list] = None,
            quick_replies: Optional[QuickReplies] = None) -> dict:
        """
        공통 응답 형태를 생성합니다.

        Args:
            content (dict | list[dict]): 'outputs'에 포함될 컨텐츠.
                                        단일 항목 또는 항목의 리스트가 될 수 있습니다.
            quick_replies (QuickReplies): 응답에 포함될 QuickReplies 객체.
        """
        # content가 단일 항목인 경우 리스트로 감싸기
        if isinstance(content, dict):
            content = [content]

        # 공통 응답 형태 구성
        template = self.create_dict_with_non_none_values(
            outputs=content if content else [],
            quickReplies=quick_replies.get_list(
                rendering=True) if quick_replies else None
        )

        # 최종 응답 형태 구성
        response = {
            'version': '2.0',
            'template': template
        }

        return response

    def render(self):
        """
        객체를 카카오톡 응답 형식에 알맞게 dict로 변환합니다.
        변환된 dict는 카카오톡 응답 형식에 맞는 최종 응답형태입니다.
        """
        self.validate()
        if self.quick_replies:
            self.quick_replies.render()

    def get_dict(self, rendering: bool = True) -> dict:
        """
        카카오톡 응답 형식에 알맞은 dict를 반환합니다.

        이 dict는 카카오톡 응답 형식에 맞는 최종 응답형태입니다.

        Returns:
            dict: 카카오톡 응답 형태의 딕셔너리
        """
        if rendering:
            self.render()
        return self.response_content_obj

    def get_json(self, ensure_ascii: bool = True, **kwargs) -> str:
        """
        카카오톡 응답 형식에 알맞은 JSON 문자열을 반환합니다.

        이 JSON은 카카오톡 응답 형식에 맞는 최종 응답형태입니다.

        Args:
            ensure_ascii (bool): json.dumps() 함수에 전달되는 인자입니다. 기본값은 True입니다.
            **kwargs: json.dumps() 함수에 전달되는 추가적인 인자들입니다.
        """
        return json.dumps(
            self.get_dict(), ensure_ascii=ensure_ascii, **kwargs
        )

    def add_quick_replies(self, quick_replies: QuickReplies) -> "BaseResponse":
        """
        QuickReplies를 추가합니다.

        Args:
            quick_replies (QuickReplies): 추가할 QuickReplies 객체

        Returns:
            BaseResponse: QuickReplies 객체가 추가된 BaseResponse 객체
        """
        if not self.quick_replies:
            self.quick_replies = quick_replies
        else:
            self.quick_replies += quick_replies
        return self

    @overload
    def add_quick_reply(self, quick_reply: QuickReply) -> "BaseResponse":
        """
        QuickReplies에 QuickReply를 객체로 추가합니다.

        Args:
            quick_reply (QuickReply): 추가할 QuickReply 객체
        """

    @overload
    def add_quick_reply(
            self,
            label: str,
            action: str,
            messageText: Optional[str] = None,
            blockId: Optional[str] = None,
            extra: Optional[dict] = None) -> "BaseResponse":
        """
        QuickReplies에 QuickReply를 인자로 객체를 생성하여 추가합니다.

        Args:
            label (str): QuickReply의 라벨
            action (str): QuickReply의 액션
            messageText (str): QuickReply의 messageText
            blockId (str): QuickReply의 blockId
            extra (dict): QuickReply의 extra
        """

    def add_quick_reply(self, *args, **kwargs) -> "BaseResponse":
        """
        QuickReplies에 QuickReply를 추가합니다.

        Args:
            *args: QuickReply 객체 또는 QuickReply 생성 인자
            **kwargs: QuickReply 객체 또는 QuickReply 생성 인자
        """
        if not self.quick_replies:
            self.quick_replies = QuickReplies()

        self.quick_replies.add_quick_reply(*args, **kwargs)
        return self

    def remove_quickReplies(self) -> "BaseResponse":
        """
        QuickReplies를 삭제합니다.

        Returns:
            BaseResponse: QuickReplies 객체가 삭제된 BaseResponse 객체
        """
        self.quick_replies = None
        return self


class ParentSkill(BaseResponse):
    """
    카카오톡 응답 형태의 객체를 생성하는 추상 클래스

    Attributes:
        response_content_obj (dict): 카카오톡 응답 형태의 객체

    Raises:
        NotImplementedError: render 또는 validate 메서드가 구현되지 않았을 때
    """
    name = "ParentSkill"  # 응답 객체의 템플릿 이름 (상속받은 클래스에서 오버라이딩 필요)

    def __init__(self, solo_mode: bool = True):
        super().__init__()
        self.solo_mode = solo_mode

    @abstractmethod
    def get_response_content(self):
        """
        각 하위 클래스에서 이 메서드를 구현하여 구체적인 응답 내용을 반환합니다.
        """

    def validate(self):
        """
        객체를 카카오톡 응답 규칙에 알맞은지 검증합니다.
        검증에 실패할 경우 예외를 발생시킵니다.

        검증 내용은 카카오톡 응답 규칙에 따라 구현되어야 합니다.

        (예) 객체 속성의 타입이 올바른지, 값이 올바른지,
            응답의 길이가 적절한지 등을 검증합니다.
        """
        if "Parent" in self.__class__.name:
            raise NotImplementedError("name 속성을 구현해야 합니다.")

    def render(self) -> dict:
        """
        객체의 응답 내용을 카카오톡 포맷에 맞게 변환합니다. 상속받은 클래스는
        get_response_content 메서드로 구체적인 내용을 정의해야 합니다.
        solo_mode가 True일 경우, 카카오톡 전체 응답 형식에 맞게 변환하여 반환합니다.
        """
        self.validate()

        if self.solo_mode:
            content = {self.__class__.name: self.get_response_content()}
            self.response_content_obj = self.create_common_response(
                content=content, quick_replies=self.quick_replies)

        else:
            self.response_content_obj = self.get_response_content()

        return self.response_content_obj

    def get_dict(self, rendering: bool = True) -> dict:
        """
        카카오톡 응답 형식에 알맞은 dict를 반환합니다.

        Returns:
            dict: 카카오톡 응답 형태의 딕셔너리
        """
        if rendering:
            self.render()
        return self.response_content_obj

    @property
    def is_empty(self) -> bool:
        """
        응답 객체가 비어있는지 여부를 반환합니다.

        Returns:
            bool: 응답 객체가 비어있으면 True, 아니면 False
        """
        return not bool(self.response_content_obj)

    @overload
    def __add__(self, other: QuickReplies) -> "ParentSkill": ...

    @overload
    def __add__(self, other: "ParentSkill") -> "KakaoResponse": ...

    def __add__(
            self,
            other: Union[QuickReplies, "ParentSkill"]
    ) -> Union["ParentSkill", "KakaoResponse"]:
        """합 연산자 정의

        QuickReplies, ParentSkill 객체를 합할 수 있습니다.
        QuickReplies 객체를 추가할 경우, 현재 객체의 QuickReplies에 해당 객체를 추가합니다.
        ParentSkill 객체를 추가할 경우, KakaoResponse 객체를 생성하여
                        현재 객체와 추가할 객체를 합친 객체를 반환합니다.

        Args:
            other : 추가할 카카오톡 응답 객체

        Returns:
            BaseResponse: 응답 객체가 추가된 BaseResponse
        """
        if isinstance(other, QuickReplies):  # QuickReplies 객체를 추가할 경우
            self.add_quick_replies(other)

        if isinstance(other, ParentSkill):  # ParentSkill 객체를 추가할 경우
            skills = SkillList(self, other)
            multi = KakaoResponse(skills)

            # 퀵리플라이가 있는 경우 합쳐줌
            if self.quick_replies:
                multi.add_quick_replies(self.quick_replies)
            if other.quick_replies:
                multi.add_quick_replies(other.quick_replies)
            return multi
        return self


class SkillList(BaseModel):
    """
    여러 ParentSkill을 합치는 클래스
    각 Skill을 카카오 응답 형식에 맞게 리스트에 담아  변환합니다.

    Args:
        ParentSkill : ParentSkill 객체들
    """

    def __init__(self, *skills: ParentSkill):
        super().__init__()
        self.skills: list[ParentSkill] = []
        if skills:
            self.skills = list(skills)
        self.response_content_obj: list[dict[str, Any]] = []
        self.set_solomode()

    def validate(self):
        """
        객체를 카카오톡 응답 규칙에 알맞은지 검증합니다.
        """
        for skill in self.skills:
            assert isinstance(skill, ParentSkill)
            assert not skill.solo_mode
            skill.validate()

    def set_solomode(self, solo_mode: bool = False):
        for skill in self.skills:
            skill.solo_mode = solo_mode

    def render(self):
        self.set_solomode()
        self.validate()
        self.response_content_obj = [
            {skill.__class__.name: skill.render()} for skill in self.skills]
        return self.response_content_obj

    def get_list(self, rendering: bool = True) -> list:
        if rendering:
            self.render()
        return self.response_content_obj

    def add_skill(self, skill: ParentSkill):
        self.skills.append(skill)
        return self

    def __add__(self, skill_list: "SkillList") -> "SkillList":
        self.skills.extend(skill_list.skills)
        return self

    def __len__(self) -> int:
        return len(self.skills)


class KakaoResponse(BaseResponse):
    def __init__(
            self,
            skill_list: Optional[SkillList] = None,
            quick_replies: Optional[QuickReplies] = None):
        super().__init__(quick_replies)
        if skill_list is None:
            skill_list = SkillList()
        self.skill_list = skill_list
        self.max_skill_count = 3

    def validate(self):
        super().validate()
        self.skill_list.validate()
        if len(self.skill_list) > self.max_skill_count:
            raise ValueError(
                f"최대 {self.max_skill_count}개의 ParentSkill을 포함할 수 있습니다.")

    def render(self):
        self.validate()
        super().render()
        self.skill_list.render()
        content_list = self.skill_list.get_list()
        self.response_content_obj = self.create_common_response(
            content=content_list, quick_replies=self.quick_replies)
        return self.response_content_obj

    def add_skill(self, skill: "ParentSkill") -> "KakaoResponse":
        """
        ParentSkill을 추가합니다.

        Args:
            skill (ParentSkill): 추가할 ParentSkill 객체

        Returns:
            BaseResponse: ParentSkill 객체가 추가된 BaseResponse 객체
        """
        from .skill import Carousel  # 순환 참조 방지
        skill.solo_mode = False
        if isinstance(skill, Carousel):
            if skill.is_empty:
                return self
            skill.set_solomode()
        self.skill_list.add_skill(skill)
        return self

    @property
    def is_empty(self) -> bool:
        """
        응답 템플릿이 비어있는지 여부를 반환합니다.

        Returns:
            bool: 응답 템플릿이 비어있으면 True, 아니면 False
        """
        return self.skill_list is None or len(self.skill_list) == 0

    @overload
    def __add__(self, other: QuickReplies) -> BaseResponse: ...

    @overload
    def __add__(self, other: ParentSkill) -> "KakaoResponse": ...

    @overload
    def __add__(self, other: SkillList) -> "KakaoResponse": ...

    @overload
    def __add__(self, other: "KakaoResponse") -> "KakaoResponse": ...

    def __add__(
            self,
            other: Union[QuickReplies, ParentSkill, SkillList, "KakaoResponse"]
    ) -> Union["KakaoResponse", BaseResponse]:
        """합 연산자 정의

        QuickReplies, ParentSkill, SkillList, KakaoResponse 객체를 합할 수 있습니다.
        QuickReplies 객체를 추가할 경우, 현재 객체의 QuickReplies에 해당 객체를 추가합니다.
        ParentSkill 객체를 추가할 경우, 현재 객체의 SkillList에 해당 객체를 추가합니다.
        SkillList 객체를 추가할 경우, 현재 객체의 SkillList에 해당 객체를 추가합니다.
        KakaoResponse 객체를 추가할 경우, 현재 객체의 SkillList에 해당 객체의 SkillList를 추가하고,
                        현재 객체의 QuickReplies에 해당 객체의 QuickReplies를 추가합니다.

        Args:
            other (QuickRelies): 추가할 QuickReplies 객체
            other (ParentSkill): 추가할 ParentSkill 객체
            other (SkillList): 추가할 SkillList 객체
            other (KakaoResponse): 추가할 KakaoResponse 객체

        Returns:
            KakaoResponse: 객체가 추가된 KakaoResponse 객체
        """
        if isinstance(other, QuickReplies):
            self.add_quick_replies(other)

        if isinstance(other, ParentSkill):
            self.add_skill(other)
            self.skill_list.set_solomode()

        if isinstance(other, SkillList):
            self.skill_list += other
            self.skill_list.set_solomode()

        if isinstance(other, KakaoResponse):
            self.skill_list += other.skill_list
            self.skill_list.set_solomode()

            # 퀵리플라이가 있는 경우 합쳐줌
            if other.quick_replies:
                self.add_quick_replies(other.quick_replies)
        return self