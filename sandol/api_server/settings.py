"""응답에 사용되는 상수들을 정의합니다."""
from .kakao.response import QuickReply
from .kakao.response.components import TextCardComponent

# 도움말 QuickReply
HELP = QuickReply(
    label="도움말",
    message_text="도움말"
)

# TIP와 E동 식당 웹페이지 TextCard
CAFETERIA_WEB = TextCardComponent(
    "TIP 및 E동", "https://ibook.kpu.ac.kr/Viewer/menu02")
