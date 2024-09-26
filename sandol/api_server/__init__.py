"""API 서버를 구성하는 모듈들

API 서버를 구성하는 모듈들이 정의되어 있습니다.
settings.py에는 환경 변수가 설정되어 있습니다.
utils.py에는 API 서버에서 사용하는 유틸리티 함수들이 정의되어 있습니다.
이외의 모듈은 각각의 API 엔드포인트를 정의하고 있습니다.
"""
from .meal import meal_api

__all__ = ["meal_api"]
