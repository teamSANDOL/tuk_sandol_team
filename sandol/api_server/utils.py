def make_TextCard(title: str, description: str) -> dict:
    """TextCard 형식의 JSON을 만들어 반환합니다."""
    return {
        "title": title,
        "description": description
    }
