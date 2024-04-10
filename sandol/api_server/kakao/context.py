"""컨텍스트 정보를 담는 클래스를 정의하는 모듈입니다.

컨텍스틑 정보는 Payload 및 Response에서 동일한 형태의 데이터로 사용되기 떄문에,
이를 통일된 형태로 관리하기 위해 별도의 클래스로 정의합니다.
"""

from typing import Optional
from .base import ParentPayload
from .common import Common
from .validation import validate_str, validate_type


class Context(ParentPayload, Common):
    """컨텍스트 정보를 담는 클래스입니다.

    컨텍스트 정보는 봇과 사용자간의 문맥적 상황 공유를 위해 사용됩니다.
    컨텍스트 정보는 이름, 남은 횟수, 유지 시간, 추가 정보를 가집니다.
    챗봇 관리자센터에서 컨텍스트를 설정하지 않으면 이 정보는 무시됩니다.

    이 클래스는 Payload와 Response에서 사용될 수 있도록 공통된 형태로 정의됩니다.
    따라서 from_dict와 render 메서드를 함께 제공합니다.

    Attributes:
        name (str): 컨텍스트의 이름
        lifespan (int): 컨텍스트의 남은 횟수
        ttl (int): 컨텍스트가 유지되는 시간
        params (dict): 컨텍스트의 추가 정보

    Examples:
    >>> context = Context(
    ...     name="context_name",
    ...     lifespan=1,
    ...     ttl=600,
    ...     params={
    ...         "key": "value"
    ...     }
    ... )
    >>> context.render()
    {
        "name": "context_name",
        "lifespan": 1,
        "ttl": 600,
        "params": {
            "key": "value"
        }
    }
    """

    def __init__(
            self,
            name: str,
            lifespan: int,
            ttl: Optional[int] = None,
            params: Optional[dict] = None):
        super().__init__()
        self.name = name
        self.lifespan = lifespan
        self.ttl = ttl
        self.params = params

    @classmethod
    def from_dict(cls, data: dict) -> 'Context':
        """딕셔너리를 Context 객체로 변환합니다.

        변환할 딕셔너리는 다음과 같은 형태입니다.
        {
            "name": "context_name",
            "lifespan": 1,
            "ttl": 600,
            "params": {
                "key": "value"
            }
        }

        Args:
            data (dict): 변환할 딕셔너리

        Returns:
            Context: 변환된 Context 객체
        """
        return cls(**data)

    def render(self) -> dict:
        """Context 객체를 카카오톡 응답 규칙에 맞게 딕셔너리로 변환합니다.

        반환되는 딕셔너리는 다음과 같은 형태입니다.
        {
            "name": "context_name",
            "lifespan": 1,
            "ttl": 600,
            "params": {
                "key": "value"
            }
        }

        Returns:
            dict: Context 객체를 변환한 딕셔너리
        """
        response = {
            "name": self.name,
            "lifespan": self.lifespan,
            "ttl": self.ttl,
            "params": self.params
        }
        return self.remove_none_item(response)

    def validate(self):
        """Context 객체의 유효성을 검사합니다.

        Raises:
            InvalidTypeError: name이 str이 아닐 경우 발생합니다.
            InvalidTypeError: lifespan이 int가 아닐 경우 발생합니다.
            InvalidTypeError: ttl이 int가 아닐 경우 발생합니다.
            InvalidTypeError: params가 dict가 아닐 경우 발생합니다.
        """
        validate_str(self.name, self.lifespan, self.ttl)
        validate_type(dict, self)
