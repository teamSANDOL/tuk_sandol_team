import re


def split_string(s: str) -> list[str]:
    """문자열을 구분자를 기준으로 분리하여 리스트로 반환합니다.

    문자열을 받아 여러 구분자를 기준으로 분리하여 리스트로 반환합니다.
    구분자는 콤마, 세미콜론, 콜론, 파이프, 대시, 슬래시입니다.

    Args:
        s (str): 분리할 문자열

    Returns:
        list: 분리된 문자열 리스트
    """
    # 여러 구분자를 개행 문자로 변경
    delimiters = [r",\s*", r";", r":", r"\|", r"-", r"/"]
    regex_pattern = '|'.join(delimiters)
    modified_str = re.sub(regex_pattern, '\n', s)

    # 개행 문자가 있는지 확인
    if '\n' in modified_str:
        # 개행 문자를 기준으로 분리하고, 각 항목의 양 끝 공백 제거
        return [
            item.strip() for item in modified_str.split('\n') if item.strip()
        ]
    else:
        # white-space를 기준으로 분리하고, 각 항목의 양 끝 공백 제거
        return [item.strip() for item in re.split(r'\s+', s) if item.strip()]
