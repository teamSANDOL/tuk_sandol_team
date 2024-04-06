from abc import ABC, abstractmethod
from typing import Optional


class BaseModel(ABC):
    """카카오 라이브러리의 대부분의 클래스의 부모 클래스

    카카오 라이브러리의 대부분의 클래스는 이 클래스를 상속받아 구현됩니다.
    create_dict_with_non_none_values 메서드를 통해 None이 아닌 값만을 가진 dict를 생성할 수 있습니다.
    render 메서드를 통해 객체를 카카오톡 응답 형식에 알맞게 dict로 변환하도록 구현해야 합니다.
    validate 메서드를 통해 카카오톡 응답 규칙에 맞는지 검증하도록 구현해야 합니다.
    """
    @staticmethod
    def create_dict_with_non_none_values(
            base: Optional[dict] = None, **kwargs):
        """value가 None이 아닌 key-value 쌍을 base에 추가해 dict를 생성합니다.

        카카오톡 서버로 반환 시 None인 값을 제외하고 반환하기 위해 사용합니다.

        Args:
            base (dict): 기본 딕셔너리, 없는 경우 빈 딕셔너리
            **kwargs: 추가할 딕셔너리

        Returns:
            dict: base와 kwargs를 합친 딕셔너리
        """
        if base is None:
            base = {}
        base.update({k: v for k, v in kwargs.items() if v is not None})
        return base

    @abstractmethod
    def render(self):
        """객체를 카카오톡 응답 형식에 알맞게 dict로 변환

        변환된 dict는 각 객체가 타깃으로 하는
        카카오톡 응답 형식의 상세 필드를 key로 가집니다.

        Returns:
            dict
        """

    @abstractmethod
    def validate(self):
        """카카오톡 응답 규칙에 알맞은지 객체를 검증

        응답 규칙에 맞지 않을 경우 예외를 발생시키도록 구현해야 합니다.
        """