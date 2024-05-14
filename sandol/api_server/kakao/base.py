"""카카오 라이브러리의 대부분의 클래스의 부모 클래스를 정의합니다.

classes:
    BaseModel: 카카오 라이브러리의 대부분의 클래스의 부모 클래스
    ParentPayload: Payload 객체의 부모 클래스
    SkillTemplate: 카카오톡 스킬 응답중 SkilllTemplate을 객체로 생성하는 추상 클래스
"""
from abc import ABC, ABCMeta, abstractmethod
import json


class BaseModel(ABC, metaclass=ABCMeta):
    """카카오 라이브러리의 대부분의 클래스의 부모 클래스

    카카오 라이브러리의 대부분의 클래스는 이 클래스를 상속받아 구현됩니다.
    remove_none_item 메서드를 통해 None이 아닌 값만을 가진 dict를 생성할 수 있습니다.
    render 메서드를 통해 객체를 카카오톡 응답 형식에 알맞게 dict로 변환하도록 구현해야 합니다.
    validate 메서드를 통해 카카오톡 응답 규칙에 맞는지 검증하도록 구현해야 합니다.
    """
    @staticmethod
    def remove_none_item(base: dict) -> dict:
        """key-value 쌍 item을 base에서 제거합니다.

        카카오톡 서버로 반환 시 None인 값을 제외하고 반환하기 위해 사용합니다.

        Args:
            base (dict): None인 값을 제거할 딕셔너리

        Returns:
            dict: None인 값을 제거한 딕셔너리
        """
        out = {}
        for key, value in base.items():
            if value is not None:
                out[key] = value
        return out

    @abstractmethod
    def render(self) -> dict | list:
        """객체를 카카오톡 응답 형식에 알맞게 dict로 변환합니다.

        변환된 dict는 각 객체가 타깃으로 하는
        카카오톡 응답 형식의 상세 필드를 key로 가집니다.
        TextCard 객체의 경우 다음과 같은 형식으로 변환됩니다:
        {
            'title': '제목',
            'description': '설명',
            'buttons': [
                {
                    'action': 'webLink',
                    'label': '링크',
                    'webLinkUrl': 'https://www.example.com',
                },
            ],
        }

        Returns:
            dict
        """

    @abstractmethod
    def validate(self):
        """카카오톡 응답 규칙에 알맞은지 객체를 검증합니다.

        응답 규칙에 맞지 않을 경우 예외를 발생시키도록 구현해야 합니다.
        """


class ParentPayload(ABC, metaclass=ABCMeta):
    """Payload 객체의 부모 클래스

    Payload 객체들의 부모 클래스로, from_json과 from_dict 메서드를 가지고 있습니다.
    Payload 객체들은 스킬 실행시 봇 시스템이 스킬 서버에게 전달하는 정보를 객체화한 것입니다.
    이 객체를 상속받는 클래스 중 Payload와 Context를 제외한 클래스들은 단독으로 사용되지 않습니다.

    from_dict 메서드를 통해 딕셔너리를 객체로 변환할 수 있도록 구현해야 합니다.
    from_json 메서드를 통해 JSON 문자열을 객체로 변환할 수 있도록 구현해야 합니다.
    """
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """딕셔너리를 객체로 변환하는 메서드

        딕셔너리를 받아서 객체로 변환하는 메서드입니다.

        Args:
            data (dict): 딕셔너리
        """

    @classmethod
    def from_json(cls, data: str):
        """JSON 문자열을 객체로 변환하는 메서드

        from_dict 메서드를 호출하여 JSON 문자열을 객체로 변환합니다.

        Args:
            data (str): JSON 문자열
        """
        return cls.from_dict(json.loads(data))


class SkillTemplate(BaseModel, metaclass=ABCMeta):
    """카카오톡 SkillTemplate 출력요소를 객체로 생성하는 추상 클래스

    BaseModel을 상속받아 구현되며, render와 validate 메서드를 구현해야 합니다.

    is_empty 프로퍼티를 통해 응답 객체가 비어있는지 여부를 확인할 수 있습니다.
    render() 메서드를 호출하여 생성된 응답 객체가 비어있는지 확인합니다.

    Raises:
        NotImplementedError: render 또는 validate 메서드가 구현되지 않았을 때

    Examples:
        >>> class TextCard(ParentComponent):
        ...     name = "textCard"   # 응답 객체의 템플릿 이름
        >>> print(TextCard.name)
        ... "textCard"
    """

    @property
    def is_empty(self) -> bool:
        """응답 객체가 비어있는지 여부를 반환합니다.

        self.render() 메서드를 호출하여 응답 객체를 생성한 후,
        응답 객체가 비어있는지 여부를 반환합니다.

        Returns:
            bool: 응답 객체가 비어있으면 True, 아니면 False
        """
        return not bool(self.render())
