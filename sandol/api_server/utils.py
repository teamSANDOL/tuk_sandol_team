def make_textcard(title: str, description: str) -> dict:
    """TextCard 형식의 JSON을 만들어 반환합니다."""
    return {
        "title": title,
        "description": description
    }


def add_quick_replies(output: dict, quick_replies: list) -> dict:
    """QuickReplies를 추가합니다.

    카카오톡 응답 형식에 알맞게 QuickReplies를 추가합니다.
    이미 QuickReplies가 존재할 경우에는 그 뒤에 추가합니다.
    ouput은 version, template 키가 있는 최상위 dict입니다.

    Args:
        output (dict): 응답 dict로 version, template 키가 있는 최상위 dict입니다.
        quick_replies (list): 추가할 QuickReplies 리스트로 각 요소는 다음과 같은 dict입니다.
            {
                "label": "사용자에게 노출될 바로가기 응답의 표시",
                "action": "바로가기 응답의 동작" (Message 혹은 Block) ,
                "messageText": "사용자 측으로 노출될 발화",
                "blockId": "동작이 Block일 경우 블록 ID" (action이 Block인 경우에만 필수)
                "extra": "동작이 Block일 경우 추가 정보" (action이 Block인 경우에만 선택)
            }

    Returns:
        dict: output에 QuickReplies가 추가된 응답 dict로 json으로 곧바로 반환하면 되는 최종 형태입니다.
    """

    # output에 quickReplies 키가 없거나 quickReplies가 비어있는 경우 초기화
    if ("quickReplies" not in output["template"] or
            not output["template"]["quickReplies"]):
        output["template"]["quickReplies"] = []

    # quickReplies 추가
    output["template"]["quickReplies"] += quick_replies
    return output


def add_help_quick_reply(output: dict) -> dict:
    """도움말 QuickReply를 추가합니다.

    도움말을 발화하는 QuickReply를 추가합니다.
    ouput은 version, template 키가 있는 최상위 dict입니다.
    add_quick_replies함수를 사용합니다.

    Args:
        output (dict): 응답 dict로 version, template 키가 있는 최상위 dict입니다.
    """
    quick_replies = [
        {
            "messageText": "도움말",
            "action": "message",
            "label": "도움말"
        }
    ]
    return add_quick_replies(output, quick_replies)
