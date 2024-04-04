from typing import Callable, Optional
from .base import BaseModel

from .common import Action, Button, Buttons, QuickReplies
from .skill import SimpleTextResponse, TextCard
from .response import KakaoResponse

from .input import Payload


class AI(BaseModel):
    def __init__(
        self,
        payload: Payload,
        callback: Optional[Callable] = None,
    ):
        self.payload = payload
        self.callback = callback
        self._answer: Optional[str] = None
        self.buttons = Buttons()
        self.buttons.max_buttons = 20
        self.ButtonWrapper = TextCard

    @staticmethod
    def create_dict_with_non_none_values(
            base: Optional[dict] = None, **kwargs):
        """
        Dict 객체를 생성합니다.
        kwargs의 값이 None이 아닌 경우 base에 추가합니다.

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

    @property
    def callback_url(self):
        return self.payload.user_request.callback_url

    @classmethod
    def from_dict(
            cls,
            user_request_dict: dict,
            callback: Optional[Callable] = None):
        payload = Payload.from_dict(user_request_dict)
        if not payload.user_request.callback_url:
            raise ValueError("Callback_url must be set")
        return cls(payload=payload, callback=callback)

    def validate(self):
        if not self.callback_url:
            raise ValueError("Callback_url must be set")

        if not self.callback:
            raise ValueError("Callback must be set")

    def set_answer(self, answer: str):
        self._answer = answer

    def add_button(self, label: str):
        button = Button(label=label, action=Action.MESSAGE, messageText=label)
        self.buttons.add_button(button)

    @property
    def answer(self):
        return self._answer

    def prepare_callback_message(
            self,
            context: Optional[dict] = None,
            data: Optional[dict] = None):
        """
        카카오 서버에 전달할 콜백 사용 여부를 나타내는 JSON 데이터를 준비합니다.

        Args:
            context (Optional[dict], optional): 콜백 사용과 관련된 컨텍스트 데이터.
            data (Optional[dict], optional): 콜백 사용과 관련된 데이터.

        Returns:
            dict: 콜백 사용 여부를 나타내는 JSON 형식의 데이터
        """
        response = {
            "version": "2.0",
            "useCallback": True,
        }

        response = self.create_dict_with_non_none_values(
            response, context=context, data=data)
        return response

    def render(self, to_json=False):
        real_response = KakaoResponse()
        if len(self.buttons) > 3:
            response = SimpleTextResponse(
                self.answer)
            real_response.add_skill(response)
            quick_replies = QuickReplies.from_buttons(self.buttons)
            real_response.add_quick_replies(quick_replies)
            return response.get_dict()

        elif len(self.buttons) == 0:
            response = SimpleTextResponse(self.answer)
            return response.get_dict()

        response = SimpleTextResponse(self.answer)
        response_card = self.ButtonWrapper(
            "Buttons",
            buttons=self.buttons,
        )
        multi_response = real_response+response+response_card
        if to_json:
            return multi_response.get_json()
        return multi_response.get_dict()
