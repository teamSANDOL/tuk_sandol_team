"""스킬 실행시 봇 시스템이 스킬 서버에게 전달하는 정보를 객체화한 Payload 객체들을 정의합니다.

classes:
    ParentPayload: Payload 객체의 부모 클래스
    Param: openbuilder에서 'detailParams'를 통해 제공되는 파라미터 정보를 저장하는 클래스
    Params: 블록의 발화에서 추출한 파라미터 정보들을 담는 클래스
    Action: payload의 'action' 항목을 받아 객체로 변환하는 클래스
    Bot: payload의 'bot' 항목을 받아 객체로 변환하는 클래스
    Knowledge: Knowledge 객체를 저장하는 클래스
    IntentExtra: Intent 객체의 extra 항목을 받아 객체로 변환하는 클래스
    Intent: payload의 'intent' 항목을 받아 객체로 변환하는 클래스
    UserProperties: 사용자의 정보를 저장하는 클래스
    User: Payload의 User 값을 저장하는 클래스
    UserRequest: Payload의 userRequest 항목을 받아 객체로 변환하는 클래스
    Payload: Payload 객체를 저장하는 클래스
"""
import json
from typing import Optional

from .base import ParentPayload
from .context import Context
from .customerror import InvalidPayloadError


class Param(ParentPayload):
    """openbuilder에서 'detailParams'를 통해 제공되는 파라미터 정보를 저장하는 클래스

    Params의 속성으로 사용되는 Param 클래스입니다.

    이 클래스는 블록의 발화로부터 추출된 개별 파라미터 정보를 담습니다. openbuilder는 파라미터 정보를
    'param'과 'detailParams'라는 두 가지 key로 구분하여 제공합니다. 이 중 'detailParams'는
    'param'에 포함된 정보와 추가적인 상세 정보를 모두 포함하고 있어, 이 클래스에서는 주로 'detailParams'
    에서 제공되는 정보를 사용합니다.

    파라미터의 값이 딕셔너리 타입인 경우, 해당 딕셔너리는 추가적인 파라미터 상세 정보를 담고 있으며,
    이 정보는 클래스의 속성으로 설정됩니다.

    Attributes:
        origin (str): 사용자 발화에서 직접 추출한 파라미터의 원본 텍스트.
        value (str | dict): 파라미터의 실제 값. 문자열 또는 딕셔너리 형태일 수 있으며,
                            딕셔너리 형태인 경우, 추가적인 상세 정보를 포함합니다.
        group_name (str): 파라미터가 속한 그룹의 이름. 파라미터를 분류하는 데 사용됩니다.
    """

    def __init__(
            self,
            origin: str,
            value: str | dict,
            group_name: str = '',
            **kwargs):
        """Param 객체를 생성하는 메서드

        Args:
            origin (str): 사용자가 입력한 발화에서 추출한 파라미터의 원본
            value (str | dict): 파라미터의 대표값
            group_name (str): 파라미터의 그룹 이름 (기본값: '')
            **kwargs: 추가적인 정보
        """
        self.origin = origin
        self.value = value
        self.group_name = group_name
        for k, v in kwargs.items():  # 추가적인 정보를 객체의 속성으로 추가
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 Param 객체를 생성하는 클래스 메서드

        이 메서드는 'detailParams'에서 제공된 파라미터 정보를 바탕으로 Param 객체를 생성합니다.
        제공된 딕셔너리는 파라미터의 'origin', 'value', 그리고 선택적으로 'groupName'을 포함할 수 있습니다.
        'value'가 딕셔너리 형태인 경우, 이는 Param 객체의 추가적인 속성으로 포함됩니다.

        Args:
            data (dict): 파라미터 정보를 포함하는 딕셔너리. 이 딕셔너리는 'origin', 'value',
                        그리고 선택적으로 'groupName' 키를 포함해야 합니다.

        Returns:
            Param: 생성된 Param 객체. 'origin', 'value', 'groupName' (있는 경우)을
                속성으로 가지며, 'value'가 딕셔너리인 경우 추가적인 속성을 동적으로 생성합니다.
        """
        try:
            origin = data.get('origin', '')
            value = data.get('value', '')
            group_name = data.get('groupName', '')
            if isinstance(value, dict):
                # 'value'가 딕셔너리 타입인 경우, 이를 객체의 속성으로 추가합니다.
                return cls(origin=origin, group_name=group_name, **value)
            else:
                return cls(origin=origin, value=value, group_name=group_name)
        except KeyError as err:
            raise InvalidPayloadError(
                'Param 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class Action(ParentPayload):
    """payload의 'action' 항목을 받아 객체로 변환하는 클래스입니다.

    Payload 객체의 action 속성으로 사용되는 클래스입니다.

    이 클래스는 사용자의 요청에 대한 액션 정보를 저장합니다. 액션 정보에는 액션의 고유 ID,
    액션의 이름, 액션에 포함된 파라미터 정보(Params 객체), 상세 파라미터 정보, 그리고
    클라이언트 추가 정보가 포함됩니다.

    Attributes:
        id (str): 액션의 고유 ID입니다.
        name (str): 액션의 이름입니다.
        params (Params): 액션에 포함된 파라미터 정보를 담는 Params 객체입니다.
        client_extra (dict): 클라이언트에서 추가적으로 제공하는 정보입니다.
    """

    def __init__(
            self,
            ID: str,  # pylint: disable=invalid-name
            name: str,
            params: dict[str, str],
            detail_params: dict[str, Param],
            client_extra: dict):
        """Action 클래스의 인스턴스를 초기화합니다.

        Args:
            id (str): 액션의 고유 ID.
            name (str): 액션의 이름.
            params (Params): 액션에 포함된 파라미터 정보.
            client_extra (dict): 클라이언트 추가 정보.
        """
        self.id = ID
        self.name = name
        self.params = params
        self.detail_params = detail_params
        self.client_extra = client_extra

    @classmethod
    def from_dict(cls, data: dict) -> 'Action':
        """딕셔너리에서 Action 객체를 생성하는 클래스 메서드입니다.

        제공해야 하는 딕셔너리는 payload의 'action'입니다.
        주어진 딕셔너리로부터 액션 정보를 추출하여 Action 클래스의 인스턴스를 생성합니다.
        필요한 모든 키가 존재하지 않는 경우, InvalidPayloadError 예외를 발생시킵니다.

        Args:
            data (dict): 액션 정보가 담긴 딕셔너리.

        Returns:
            Action: 생성된 Action 인스턴스.
        """
        ID = data.get('id', '')  # pylint: disable=invalid-name
        name = data.get('name', '')
        params = data.get('params', {})
        print(data.get('detailParams', {}))
        detail_params = {
            key: Param.from_dict(value)
            for key, value in data.get('detailParams', {}).items()
        }
        client_extra = data['clientExtra']
        return cls(
            ID=ID,
            name=name,
            params=params,
            detail_params=detail_params,
            client_extra=client_extra
        )


class Bot(ParentPayload):
    """payload의 'bot' 항목을 받아 객체로 변환하는 클래스입니다.

    Payload 객체의 bot 속성으로 사용되는 클래스입니다.
    이 클래스는 봇 정보를 저장합니다. 봇 정보에는 봇의 고유 ID와 이름이 포함됩니다.

    Attributes:
        id (str): 봇의 고유 ID입니다.
        name (str): 봇의 이름입니다.
    """

    def __init__(self, ID: str, name: str):  # pylint: disable=invalid-name
        """Bot 클래스의 인스턴스를 초기화합니다.

        Args:
            id (str): 봇의 고유 ID.
            name (str): 봇의 이름.
        """
        self.id = ID
        self.name = name

    @classmethod
    def from_dict(cls, data: dict) -> 'Bot':
        """딕셔너리에서 Bot 객체를 생성하는 클래스 메서드입니다.

        제공해야 하는 딕셔너리는 payload의 'bot'입니다.
        주어진 딕셔너리로부터 봇 정보를 추출하여 Bot 클래스의 인스턴스를 생성합니다.
        필요한 모든 키가 존재하지 않는 경우, InvalidPayloadError 예외를 발생시킵니다.

        Args:
            data (dict): 봇 정보가 담긴 딕셔너리.

        Returns:
            Bot: 생성된 Bot 인스턴스.
        """
        ID = data.get("id", '')  # pylint: disable=invalid-name
        name = data.get("name", '')
        return cls(
            ID=ID,
            name=name
        )


class Knowledge(ParentPayload):
    """Knowledge 객체를 저장하는 클래스입니다.

    IntentExtra의 matched_knowledges 속성으로 사용되는 클래스입니다.
    이 클래스는 지식+의 지식 정보를 저장합니다.
    발화와 일치하는 지식의 정보를 담기 위해 사용됩니다.
    지식 정보에는 지식의 ID, 이름, 설명, 그리고 추가 정보가 포함됩니다.

    Attributes:
        answer (str): 지식의 답변입니다.
        question (str): 지식의 질문입니다.
        categories (list[str]): 지식의 카테고리입니다.
        landing_url (str): 지식 답변에서 링크 더보기 url 입니다.
        image_url (str): 지식 답변에서 썸네일 이미지 url 입니다.
    """

    def __init__(
            self,
            answer: str,
            question: str,
            categories: list[str],
            landing_url: str,
            image_url: str):
        """Knowledge 클래스의 인스턴스를 초기화합니다."""
        self.answer = answer
        self.question = question
        self.categories = categories
        self.landing_url = landing_url
        self.image_url = image_url

    @classmethod
    def from_dict(cls, data: dict) -> 'Knowledge':
        """딕셔너리에서 Knowledge 객체를 생성하는 클래스 메서드입니다.

        제공해야 하는 딕셔너리는 payload의 'intent'의 'extra'의
        'matched_knowledges' 배열의 요소 입니다.
        주어진 딕셔너리로부터 지식 정보를 추출하여 Knowledge 클래스의 인스턴스를 생성합니다.
        IntentExtra 객체의 'matched_knowledges' 의 배열 속성으로 사용됩니다.

        Args:
            data (dict): 지식 정보가 담긴 딕셔너리.
        """
        answer = data.get('answer', '')
        question = data.get('question', '')
        categories = data.get('categories', [])
        landing_url = data.get('landingUrl', '')
        image_url = data.get('imageUrl', '')
        return cls(
            answer=answer,
            question=question,
            categories=categories,
            landing_url=landing_url,
            image_url=image_url
        )


class IntentExtra(ParentPayload):
    """Intent 객체의 extra 항목을 받아 객체로 변환하는 클래스입니다.

    이 클래스는 Intent 객체의 extra 속성으로 사용됩니다.
    extra 항목에는 발화에서 지식+와 일치하는 지식의 목록을 담고 있습니다.
    Payload의 'intent' 항목에서 'extra'를 받아 객체로 변환하기 위해 사용됩니다.

    Attributes:
        reson (dict): 정보 없음(Kakao에서 정보를 제공하지 않습니다.)
        matched_knowledges (dict): Intent의 지식을 나타내는 딕셔너리입니다.
    """

    def __init__(
            self,
            reson: Optional[dict] = None,
            matched_knowledges: Optional[list[Knowledge]] = None):
        """IntentExtra 클래스의 인스턴스를 초기화합니다.

        Args:
            reson (dict): 정보 없음(Kakao에서 정보를 제공하지 않습니다.)
            matched_knowledges (dict): Intent의 지식을 나타내는 딕셔너리.
        """
        if reson is None:
            reson = {}
        self.reson = reson
        self.matched_knowledges = matched_knowledges

    @classmethod
    def from_dict(cls, data: dict) -> 'IntentExtra':
        """딕셔너리에서 IntentExtra 객체를 생성하는 클래스 메서드입니다.

        제공해야 하는 딕셔너리는 payload의 'intent'의 'extra'입니다.
        주어진 딕셔너리로부터 IntentExtra 정보를 추출하여 IntentExtra 클래스의 인스턴스를 생성합니다.

        Args:
            data (dict): IntentExtra 정보가 담긴 딕셔너리.
        """
        reason: dict = data.get('reason', {})
        knowledges: dict = data.get('matched_knowledges', {})
        matched_knowledges = [Knowledge.from_dict(
            knowledge) for knowledge in knowledges]
        return cls(reason, matched_knowledges)


class Intent(ParentPayload):
    """payload의 'intent' 항목을 받아 객체로 변환하는 클래스입니다.

    Payload 객체의 intent 속성으로 사용되는 클래스입니다.
    발화와 일치하는 블록이나 지식의 정보를 담고 있는 객체입니다.
    발화가 지식+에 일치하는 경우, 일치하는 지식의 목록을 포함합니다.
    extra는 발화에 일치한 지식 목록을 포함하는 IntentExtra 객체로 구성됩니다.

    Attributes:
        id (str): Intent의 고유 ID입니다.
        name (str): Intent의 이름입니다.
        extra (IntentExtra): Intent의 추가 정보입니다.
    """

    def __init__(
            self,
            ID: str,  # pylint: disable=invalid-name
            name: str,
            extra: IntentExtra):
        """Intent 클래스의 인스턴스를 초기화합니다."""
        self.id = ID
        self.name = name
        self.extra = extra

    @classmethod
    def from_dict(cls, data: dict) -> 'Intent':
        """딕셔너리에서 Intent 객체를 생성하는 클래스 메서드입니다.

        제공해야 하는 딕셔너리는 payload의 'intent'입니다.
        주어진 딕셔너리로부터 Intent 정보를 추출하여 Intent 클래스의 인스턴스를 생성합니다.

        Args:
            data (dict): Intent 정보가 담긴 딕셔너리.

        Returns:
            Intent: 생성된 Intent 인스턴스.
        """
        ID = data.get('id', '')  # pylint: disable=invalid-name
        name = data.get('name', '')
        extra = IntentExtra.from_dict(data.get('extra', {}))
        return cls(
            ID=ID,
            name=name,
            extra=extra
        )


class UserProperties(ParentPayload):
    """사용자의 정보를 저장하는 클래스입니다.

    UserRequest 객체의 user 속성으로 사용됩니다.
    추가적으로 제공하는 사용자의 속성 정보를 담고 있습니다.

    Attributes:
        plusfriend_user_key (str): 카카오톡 채널에서 제공하는 사용자 식별키
        app_user_id (str): 봇 설정에서 앱키를 설정한 경우에만 제공되는 사용자 정보입니다.
        is_friend (bool): 사용자가 봇과 연결된 카카오톡 채널을 추가한 경우 제공되는 식별키입니다.
    """

    def __init__(
            self,
            plusfriend_user_key: str,
            app_user_id: str,
            is_friend: bool):
        """UserProperties 객체를 생성하는 메서드"""
        self.plusfriend_user_key = plusfriend_user_key
        self.app_user_id = app_user_id
        self.is_friend = is_friend

    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 UserProperties 객체를 생성하는 클래스 메서드

        전달받는 딕셔너리는 payload의 'user'의 'properties'입니다.
        주어진 딕셔너리로부터 사용자 정보를 추출하여 UserProperties 클래스의 인스턴스를 생성합니다.

        Args:
            data (dict): 사용자 정보가 담긴 딕셔너리
        """
        plusfriend_user_key = data.get('plusfriendUserKey', '')
        app_user_id = data.get('appUserId', '')
        is_friend = data.get('isFriend', '')
        return cls(
            plusfriend_user_key=plusfriend_user_key,
            app_user_id=app_user_id,
            is_friend=is_friend
        )


class User(ParentPayload):
    """Payload의 User 값을 저장하는 클래스입니다.

    UserRequest 객체의 user 속성으로 사용됩니다.

    Attributes:
        id (str): 사용자를 식별할 수 있는 key로 최대 70자의 값
        type (str): 현재는 botUserKey만 제공
        properties (dict): 추가적으로 제공하는 사용자의 속성 정보
    """

    def __init__(
            self,
            ID: str,  # pylint: disable=invalid-name
            TYPE: str,  # pylint: disable=invalid-name
            properties: Optional[dict] = None):
        """User 객체를 생성하는 메서드

        properties가 None인 경우 빈 딕셔너리로 초기화합니다.
        """
        if properties is None:
            properties = {}

        self.id = ID
        self.type = TYPE
        self.properties = properties

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """딕셔너리에서 User 객체를 생성하는 클래스 메서드

        전달받는 딕셔너리는 payload의 'userRequest'의 'user'입니다.

        Args:
            data (dict): 사용자 정보가 담긴 딕셔너리

        Returns:
            User: 생성된 User 객체
        """
        ID = data.get('id', '')  # pylint: disable=invalid-name
        TYPE = data.get('type', '')  # pylint: disable=invalid-name
        properties = data.get('properties', {})
        return cls(
            ID=ID,
            TYPE=TYPE,
            properties=properties
        )


class UserRequest(ParentPayload):
    """Payload의 userRequest 항목을 받아 객체로 변환하는 클래스입니다.

    Payload 객체의 user_request 속성으로 사용됩니다.

    Attributes:
        timezone (str): 사용자의 시간대
        block (dict): 사용자의 발화에 반응한 블록의 정보 (id, name)
        utterance (str): 사용자 발화
        lang (str): 사용자 발화의 언어, 한국에서 보낸 요청이라면 “ko”
        user (User): 사용자 정보
        params (dict): 정보 없음(Kakao에서 정보를 제공하지 않습니다.)
        callback_url (str): AI 콜백 요청을 전송할 URL
    """

    def __init__(
            self,
            timezone: str,
            block: dict,
            utterance: str,
            lang: str,
            user: User,
            params: Optional[dict] = None,
            callback_url: Optional[str] = None):
        """UserRequest 객체를 생성하는 메서드"""
        self.timezone = timezone
        self.block = block
        self.utterance = utterance
        self.lang = lang
        self.user = user
        self.params = params
        self.callback_url = callback_url

    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 UserRequest 객체를 생성하는 클래스 메서드

        전달받는 딕셔너리는 payload의 'userRequest'입니다.

        Args:
            data (dict): 사용자 요청 정보가 담긴 딕셔너리
        """
        timezone = data.get('timezone', '')
        block = data.get('block', {})
        utterance = data.get('utterance', '')
        lang = data.get('lang', '')
        user = User.from_dict(data.get('user', {}))
        params = data.get('params')
        callback_url = data.get('callbackUrl')
        return cls(
            timezone=timezone,
            block=block,
            utterance=utterance,
            lang=lang,
            user=user,
            params=params,
            callback_url=callback_url
        )


class Payload(ParentPayload):
    """Payload 객체를 저장하는 클래스입니다.

    Payload 객체는 스킬 실행시 봇 시스템이 스킬 서버에게 전달하는 정보를 객체화한 것입니다.
    이 클래스는 Intent, UserRequest, Bot, Action 객체를 속성으로 가지고 있습니다.
    스킬 서버에서 전달받은 json 데이터 또는 dict 데이터를 곧바로 Payload 객체로 변환할 수 있습니다.

    Attributes:
        intent (Intent): 발화와 일치하는 블록이나 지식의 정보를 담고 있는 객체
        user_request (UserRequest): 사용자의 요청 정보를 담고 있는 객체
        bot (Bot): 봇 정보를 담고 있는 객체
        action (Action): 사용자의 요청에 대한 액션 정보를 담고 있는 객체
        contexts (list[Context]): 컨텍스트 정보를 담고 있는 객체 배열

    Properties:
        user_id (str): 사용자의 ID == user_request.user.id
        params (Params): 액션에 포함된 파라미터 정보 == action.params
        utterance (str): 사용자 발화
    """

    def __init__(
            self,
            intent: Intent,
            user_request: UserRequest,
            bot: Bot,
            action: Action,
            contexts: Optional[list] = None):
        """Payload 객체를 생성하는 메서드

        context가 None인 경우 빈 딕셔너리로 초기화합니다.
        """
        self.intent = intent
        self.user_request = user_request
        self.bot = bot
        self.action = action
        if contexts is None:
            contexts = []
        self.contexts = contexts

    @classmethod
    def from_dict(cls, data: dict) -> 'Payload':
        """딕셔너리에서 Payload 객체를 생성하는 클래스 메서드

        전달받는 딕셔너리는 skill server에서 전달받은 전체 data입니다.

        Args:
            data (dict): payload 정보가 담긴 딕셔너리

        Returns:
            Payload: 생성된 Payload 객체
        """

        intent = Intent.from_dict(data.get('intent', {}))
        user_request = UserRequest.from_dict(data.get('userRequest', {}))
        bot = Bot.from_dict(data.get('bot', {}))
        action = Action.from_dict(data.get('action', {}))
        contexts = [Context.from_dict(context)
                    for context in data.get('contexts', [])]
        return cls(
            intent=intent,
            user_request=user_request,
            bot=bot,
            action=action,
            contexts=contexts
        )

    @classmethod
    def from_json(cls, data: str) -> 'Payload':
        """JSON 문자열을 Payload 객체로 변환하는 클래스 메서드

        전달받는 json 문자열은 skill server에서 전달받은 전체 data입니다.
        from_dict 메서드를 호출하여 JSON 문자열을 객체로 변환합니다.

        Args:
            data (str): JSON 문자열
        """
        return cls.from_dict(json.loads(data))

    @property
    def user_id(self):
        """사용자의 ID를 반환합니다.

        사용자의 ID는 user_request.user.id로부터 가져옵니다.

        Returns:
            str: 사용자의 ID
            """
        if (
            hasattr(self, 'user_request') and
            hasattr(self.user_request, 'user') and
            hasattr(self.user_request.user, 'id')
        ):
            return self.user_request.user.id
        return None

    @property
    def params(self):
        """액션에 포함된 파라미터 정보를 반환합니다.

        액션에 포함된 파라미터 정보는 action.params로부터 가져옵니다.

        Returns:
            Params: 액션에 포함된 파라미터 정보
            None: 액션이 없거나 파라미터 정보가 없는 경우
        """
        if hasattr(self, 'action') and hasattr(self.action, 'params'):
            return self.action.params
        return None

    @property
    def detail_params(self):
        """액션에 포함된 파라미터 세부 정보를 반환합니다.

        액션에 포함된 파라미터 세부 정보는 action.detail_params로부터 가져옵니다.

        Returns:
            dict: 액션에 포함된 파라미터 세부 정보
            None: 액션이 없거나 파라미터 세부 정보가 없는 경우
        """
        if hasattr(self, 'action') and hasattr(self.action, 'detail_params'):
            return self.action.detail_params
        return None

    @property
    def utterance(self):
        """사용자 발화를 반환합니다.

        사용자 발화는 user_request.utterance로부터 가져옵니다.

        Returns:
            str: 사용자 발화
            None: 사용자 발화 정보가 없는 경우
        """
        if (hasattr(self, 'user_request') and
                hasattr(self.user_request, 'utterance')):
            return self.user_request.utterance
        return None
