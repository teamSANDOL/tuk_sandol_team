"""응답에 사용되는 상수들을 정의합니다."""
from .kakao.response import QuickReply
from .kakao.response.components import TextCardComponent
from .kakao.response.interactiron import ActionEnum

# 도움말 QuickReply
HELP = QuickReply(
    label="도움말",
    message_text="도움말"
)

# TIP와 E동 식당 웹페이지 TextCard
CAFETERIA_WEB = TextCardComponent(
    "TIP 및 E동", "https://ibook.kpu.ac.kr/Viewer/menu02")

# 퀵리플라이 정의
ADD_LUNCH_QUICK_REPLY = QuickReply(
    "점심 메뉴 추가", ActionEnum.BLOCK, block_id="660e009c30bfc84fad05dcbf")
ADD_DINNER_QUICK_REPLY = QuickReply(
    "저녁 메뉴 추가", ActionEnum.BLOCK, block_id="660e00a8d837db3443451ef9")
SUBMIT_QUICK_REPLY = QuickReply(
    "확정", ActionEnum.BLOCK, block_id="661bccff4df3202baf9e8bdd")
DELETE_MENU_QUICK_REPLY = QuickReply(
    "메뉴 삭제", ActionEnum.BLOCK, block_id="66438b74334aaa30751802e9")
DELETE_EVERY_QUICK_REPLY = QuickReply(
    "모든 메뉴 삭제", ActionEnum.BLOCK, block_id="6643a2ce0431eb378ea12748")