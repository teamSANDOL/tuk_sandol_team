"""Kakao Response를 처리하기 위한 유틸리티 함수들을 제공합니다."""
import re

# 카멜 케이스 문자열을 스네이크 케이스 문자열로 변환하기 위한 정규식 패턴
CamelToSnakePattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_snake(camel: str) -> str:
    """카멜 케이스 문자열을 스네이크 케이스 문자열로 변환합니다.

    Args:
        camel (str): 카멜 케이스 문자열

    Returns:
        str: 스네이크 케이스 문자열
    """
    return CamelToSnakePattern.sub('_', camel).lower()


if __name__ == "__main__":
    print(camel_to_snake("CamelCase"))
    print(camel_to_snake("CamelCaseTest"))
    print(camel_to_snake("camelCase"))
    print(camel_to_snake("camelCaseTest"))
