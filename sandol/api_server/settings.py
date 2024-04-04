from .kakao.response import QuickReply
from .kakao.skill import TextCard

# 도움말 QuickReply
HELP = QuickReply(
    label="도움말",
    messageText="도움말"
)

# TIP와 E동 식당 웹페이지 TextCard
CAFETERIA_WEB = TextCard(
    "TIP 및 E동", "https://ibook.kpu.ac.kr/Viewer/menu01")
