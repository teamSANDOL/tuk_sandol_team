"""응답에 사용되는 상수들을 정의합니다."""
import logging

from kakao_chatbot.response import QuickReply, ActionEnum
from kakao_chatbot.response.components import TextCardComponent

# 도움말 QuickReply
HELP = QuickReply(
    label="도움말",
    message_text="도움말"
)

# TIP와 E동 식당 웹페이지 TextCard
CAFETERIA_WEB = TextCardComponent(
    "TIP 및 E동", "https://ibook.kpu.ac.kr/Viewer/menu02")

# 퀵리플라이 정의
CAFETRIA_REGISTER_QUICK_REPLY_LIST = [
    QuickReply(
        "확정", ActionEnum.BLOCK, block_id="661bccff4df3202baf9e8bdd"),
    QuickReply(
        "점심 메뉴 추가", ActionEnum.BLOCK, block_id="660e009c30bfc84fad05dcbf"),
    QuickReply(
        "저녁 메뉴 추가", ActionEnum.BLOCK, block_id="660e00a8d837db3443451ef9"),
    QuickReply(
        "메뉴 삭제", ActionEnum.BLOCK, block_id="66438b74334aaa30751802e9"),
    QuickReply(
        "모든 메뉴 삭제", ActionEnum.BLOCK, block_id="6643a2ce0431eb378ea12748")
]

# 식당별 네이버 지도 URL
NAVER_MAP_URL_DICT = {
    "미가식당": "https://naver.me/xEMZ6QdE",
    "세미콘식당": "https://naver.me/xQ8Khcho",
    "산돌식당": "https://naver.me/xEMZ6QdE",
    "TIP 가가식당": "https://naver.me/GCaFzr8k",
    "E동 레스토랑": "https://naver.me/GRO427Hk",
    "수호식당": "https://naver.me/Gz18OrEt",
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("sandol_logger")
