from abc import ABC, abstractmethod
import json
from typing import Optional

from .customerror import InvalidPayloadError


class ParentPayload(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, json_payload: str): ...

    @classmethod
    @abstractmethod
    def from_dict(cls, dict_payload: dict): ...


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
    def from_json(cls, detail_param_json: str):
        detail_param_dict = json.loads(detail_param_json)
        return cls.from_dict(detail_param_dict)

    @classmethod
    def from_dict(cls, detail_param_dict: dict):
        # value가 딕셔너리 타입이면, 이를 **kwargs로 전달
        additional_params = detail_param_dict['value'] if isinstance(
            detail_param_dict.get('value'), dict) else {}
        try:
            origin = detail_param_dict['origin']
            value = detail_param_dict['value']
            group_name = detail_param_dict['groupName']
            return cls(
                origin=origin,
                value=value,
                group_name=group_name,
                **additional_params
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "Param 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


class Params(ParentPayload):
    def __init__(self, **kwargs: dict[str, Param]):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_json(cls, action_json: str):
        params_dict = json.loads(action_json)
        return cls.from_dict(params_dict)

    @classmethod
    def from_dict(cls, action_dict: dict):
        params = {
            key: Param.from_dict(value)
            for key, value in action_dict.get("detailParams", {}).items()
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
    def from_json(cls, action_json: str):
        action_dict = json.loads(action_json)
        return cls.from_dict(action_dict)

    @classmethod
    def from_dict(cls, action_dict: dict):
        try:
            _id = action_dict['id']
            name = action_dict['name']
            params = Params.from_dict(action_dict)
            detail_params = action_dict['detailParams']
            client_extra = action_dict['clientExtra']
            return cls(
                id=_id,
                name=name,
                params=params,
                detail_params=detail_params,
                client_extra=client_extra
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "Action 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


class Bot(ParentPayload):
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_json(cls, bot_json: str):
        bot_dict = json.loads(bot_json)
        return cls.from_dict(bot_dict)

    @classmethod
    def from_dict(cls, bot_dict: dict):
        try:
            _id = bot_dict['id']
            name = bot_dict['name']
            return cls(
                id=_id,
                name=name
            )
        except KeyError as err:
            raise InvalidPayloadError("Bot 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


class IntentExtra(ParentPayload):
    def __init__(self, reason: dict, knowledge: dict | None = None):
        self.reason = reason
        self.knowledge = knowledge

    @classmethod
    def from_json(cls, intent_extra_json: str):
        intent_extra_dict = json.loads(intent_extra_json)
        return cls.from_dict(intent_extra_dict)

    @classmethod
    def from_dict(cls, intent_extra_dict: dict):
        try:
            reason = intent_extra_dict['reason']
            knowledge = intent_extra_dict.get('knowledge')
            return cls(
                reason=reason,
                knowledge=knowledge
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "IntentExtra 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


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
    def from_json(cls, intent_json: str):
        intent_dict = json.loads(intent_json)
        return cls.from_dict(intent_dict)

    @classmethod
    def from_dict(cls, intent_dict: dict):
        try:
            _id = intent_dict['id']
            name = intent_dict['name']
            extra = IntentExtra.from_dict(intent_dict['extra'])
            return cls(
                id=_id,
                name=name,
                extra=extra
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "Intent 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


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
    def from_dict(cls, user_properties_dict: dict):
        try:
            plusfriend_user_key = user_properties_dict['plusfriendUserKey']
            app_user_id = user_properties_dict['appUserId']
            is_friend = user_properties_dict['isFriend']
            return cls(
                plusfriend_user_key=plusfriend_user_key,
                app_user_id=app_user_id,
                is_friend=is_friend
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "UserProperties 객체를 생성하기 위한 키가 존재하지 않습니다.") from err

    @classmethod
    def from_json(cls, user_properties_json: str):
        user_properties_dict = json.loads(user_properties_json)
        return cls.from_dict(user_properties_dict)


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
    def from_json(cls, user_request_json: str):
        user_request_dict = json.loads(user_request_json)
        return cls.from_dict(user_request_dict)

    @classmethod
    def from_dict(cls, user_request_dict: dict):
        try:
            _id = user_request_dict['id']
            _type = user_request_dict['type']
            properties = user_request_dict.get('properties', {})
            return cls(
                id=_id,
                type=_type,
                properties=properties
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "User 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


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
    def from_json(cls, user_request_json: str):
        user_request_dict = json.loads(user_request_json)
        return cls.from_dict(user_request_dict)

    @classmethod
    def from_dict(cls, user_request_dict: dict):
        try:
            timezone = user_request_dict['timezone']
            block = user_request_dict['block']
            utterance = user_request_dict['utterance']
            lang = user_request_dict['lang']
            user = User.from_dict(user_request_dict['user'])
            params = user_request_dict['params']
            callback_url = user_request_dict.get('callbackUrl')
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
                "UserRequest 객체를 생성하기 위한 키가 존재하지 않습니다.") from err


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
    def from_json(cls, payload_json: str):
        payload_dict = json.loads(payload_json)
        return cls.from_dict(payload_dict)

    @classmethod
    def from_dict(cls, payload_dict: dict):
        try:
            intent = Intent.from_dict(payload_dict['intent'])
            user_request = UserRequest.from_dict(payload_dict['userRequest'])
            bot = Bot.from_dict(payload_dict['bot'])
            action = Action.from_dict(payload_dict['action'])
            return cls(
                intent=intent,
                user_request=user_request,
                bot=bot,
                action=action
            )
        except KeyError as err:
            raise InvalidPayloadError(
                "Payload 객체를 생성하기 위한 키가 존재하지 않습니다.") from err

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
