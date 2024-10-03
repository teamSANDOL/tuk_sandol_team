"""카카오톡 챗봇을 개발하기 위한 라이브러리입니다.

Packages:
    response: 카카오톡 응답 규칙에 맞는 응답 객체들을 정의합니다.

Modules:
    base: 라이브러리의 기본 부모 클래스(BaseModel)와 스킬 템플릿(SkillTemplate)을 정의합니다.
    context: 컨텍스트 정보를 담는 클래스를 정의합니다.
    customerror: 사용자 정의 예외를 정의합니다.
    input: 스킬 실행시 봇 시스템이 스킬 서버에게 전달하는 정보를 객체화한 Payload 객체들을 정의합니다.
    utils: 라이브러리에서 사용하는 유틸리티 함수들을 정의합니다.
    validation: 라이브러리에서 사용하는 유효성 검사 함수들을 정의합니다.
"""
from .base import BaseModel
from . import response
from .customerror import InvalidLinkError, InvalidTypeError, InvalidActionError
from .input import Payload, ValidationPayload

__all__ = [
    "response",
    "InvalidActionError", "InvalidLinkError", "InvalidTypeError",
    "Payload", "ValidationPayload"
]
