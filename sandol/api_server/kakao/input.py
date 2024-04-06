from abc import ABC, abstractmethod
import json
from typing import Optional

from .customerror import InvalidPayloadError


class ParentPayload(ABC):
    @classmethod
    def from_json(cls, data: str):
        return cls.from_dict(json.loads(data))

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict): ...


class Param(ParentPayload):
    def __init__(
            self,
            origin: str,
            value: str | dict,
            group_name: str = '',
            **kwargs):
        self.origin = origin
        self.value = value
        self.group_name = group_name
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: dict):
        # value가 딕셔너리 타입이면, 이를 **kwargs로 전달
        additional_params = data['value'] if isinstance(
            data.get('value'), dict) else {}
        try:
            origin = data['origin']
            value = data['value']
            group_name = data['groupName']
            return cls(
                origin=origin,
                value=value,
                group_name=group_name,
                **additional_params
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'Param 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class Params(ParentPayload):
    def __init__(self, **kwargs: dict[str, Param]):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: dict):
        params = {
            key: Param.from_dict(value)
            for key, value in data.get('detailParams', {}).items()
        }
        return cls(**params)

    def to_dict(self):
        return {
            key: value.__dict__
            for key, value in self.__dict__.items()
        }

    def __iter__(self):
        return iter(self.__dict__.items())

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()


class Action(ParentPayload):
    def __init__(
            self,
            id: str,
            name: str,
            params: Params,
            detail_params: dict,
            client_extra: dict):
        self.id = id
        self.name = name
        self.params = params
        self.detailParams = detail_params
        self.clientExtra = client_extra

    @classmethod
    def from_dict(cls, data: dict):
        try:
            _id = data['id']
            name = data['name']
            params = Params.from_dict(data)
            detail_params = data['detailParams']
            client_extra = data['clientExtra']
            return cls(
                id=_id,
                name=name,
                params=params,
                detail_params=detail_params,
                client_extra=client_extra
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'Action 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class Bot(ParentPayload):
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data: dict):
        try:
            _id = data['id']
            name = data['name']
            return cls(
                id=_id,
                name=name
            )
        except KeyError as err:
            raise InvalidPayloadError('Bot 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class IntentExtra(ParentPayload):
    def __init__(self, reason: dict, knowledge: dict | None = None):
        self.reason = reason
        self.knowledge = knowledge

    @classmethod
    def from_dict(cls, data: dict):
        try:
            reason = data['reason']
            knowledge = data.get('knowledge')
            return cls(
                reason=reason,
                knowledge=knowledge
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'IntentExtra 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class Intent(ParentPayload):
    def __init__(
            self,
            id: str,
            name: str,
            extra: dict):
        self.id = id
        self.name = name
        self.extra = extra

    @classmethod
    def from_dict(cls, data: dict):
        try:
            _id = data['id']
            name = data['name']
            extra = IntentExtra.from_dict(data['extra'])
            return cls(
                id=_id,
                name=name,
                extra=extra
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'Intent 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class UserProperties(ParentPayload):
    def __init__(
            self,
            plusfriend_user_key: str,
            app_user_id: str,
            is_friend: bool):

        self.plusfriend_user_key = plusfriend_user_key
        self.app_user_id = app_user_id
        self.is_friend = is_friend

    @classmethod
    def from_dict(cls, data: dict):
        try:
            plusfriend_user_key = data['plusfriendUserKey']
            app_user_id = data['appUserId']
            is_friend = data['isFriend']
            return cls(
                plusfriend_user_key=plusfriend_user_key,
                app_user_id=app_user_id,
                is_friend=is_friend
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'UserProperties 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class User(ParentPayload):
    def __init__(
            self,
            id: str,
            type: str,
            properties: Optional[dict] = None):

        if properties is None:
            properties = {}

        self.id = id
        self.type = type
        self.properties = properties

    @classmethod
    def from_dict(cls, data: dict):
        try:
            _id = data['id']
            _type = data['type']
            properties = data.get('properties', {})
            return cls(
                id=_id,
                type=_type,
                properties=properties
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'User 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class UserRequest(ParentPayload):
    def __init__(
            self,
            timezone: str,
            block: dict,
            utterance: str,
            lang: str,
            user: User,
            params: dict,
            callback_url: Optional[str] = None):
        self.timezone = timezone
        self.block = block
        self.utterance = utterance
        self.lang = lang
        self.user = user
        self.params = params
        self.callback_url = callback_url

    @classmethod
    def from_dict(cls, data: dict):
        try:
            timezone = data['timezone']
            block = data['block']
            utterance = data['utterance']
            lang = data['lang']
            user = User.from_dict(data['user'])
            params = data['params']
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
        except KeyError as err:
            raise InvalidPayloadError(
                'UserRequest 객체를 생성하기 위한 키가 존재하지 않습니다.') from err


class Payload(ParentPayload):
    def __init__(
            self,
            intent: Intent,
            user_request: UserRequest,
            bot: Bot,
            action: Action):
        self.intent = intent
        self.user_request = user_request
        self.bot = bot
        self.action = action

    @classmethod
    def from_dict(cls, data: dict):
        try:
            intent = Intent.from_dict(data['intent'])
            user_request = UserRequest.from_dict(data['userRequest'])
            bot = Bot.from_dict(data['bot'])
            action = Action.from_dict(data['action'])
            return cls(
                intent=intent,
                user_request=user_request,
                bot=bot,
                action=action
            )
        except KeyError as err:
            raise InvalidPayloadError(
                'Payload 객체를 생성하기 위한 키가 존재하지 않습니다.') from err

    @property
    def user_id(self):
        if (
            hasattr(self, 'user_request') and
            hasattr(self.user_request, 'user') and
            hasattr(self.user_request.user, 'id')
        ):
            return self.user_request.user.id
        return None

    @property
    def params(self):
        if hasattr(self, 'action') and hasattr(self.action, 'params'):
            return self.action.params
        return None