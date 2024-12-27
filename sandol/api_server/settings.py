"""응답에 사용되는 상수들을 정의합니다."""

import logging

from kakao_chatbot.response import QuickReply, ActionEnum
from kakao_chatbot.response.components import TextCardComponent

# 도움말 QuickReply
HELP = QuickReply(label="도움말", message_text="도움말")

# TIP와 E동 식당 웹페이지 TextCard
CAFETERIA_WEB = TextCardComponent(
    "TIP 및 E동", "https://ibook.kpu.ac.kr/Viewer/menu02")

# 블록 ID 관리
BLOCK_IDS = {
    "confirm": "6721838c369c0a05baca37a1",
    "add_lunch_menu": "672181220b8411112c75c884",
    "add_dinner_menu": "672181305e0ed128077abf5e",
    "delete_menu": "67218142369c0a05baca376c", 
    "delete_all_menus": "6721837657cc8a7ef53213ef",
    "approve_restaurant": "6731d9b89fb8545410e9d29b",
    "decline_restaurant": "674031c1aeded40bd4bd58d9",
}

# 퀵리플라이 정의
CAFETRIA_REGISTER_QUICK_REPLY_LIST = [
    QuickReply("확정", ActionEnum.BLOCK, block_id=BLOCK_IDS["confirm"]),
    QuickReply("점심 메뉴 추가", ActionEnum.BLOCK,
               block_id=BLOCK_IDS["add_lunch_menu"]),
    QuickReply("저녁 메뉴 추가", ActionEnum.BLOCK,
               block_id=BLOCK_IDS["add_dinner_menu"]),
    QuickReply("메뉴 삭제", ActionEnum.BLOCK, block_id=BLOCK_IDS["delete_menu"]),
    QuickReply("모든 메뉴 삭제", ActionEnum.BLOCK,
               block_id=BLOCK_IDS["delete_all_menus"]),
]

# 식당별 네이버 지도 URL
NAVER_MAP_URL_DICT = {
    "미가식당": "https://naver.me/xEMZ6QdE",
    "세미콘식당": "https://naver.me/xQ8Khcho",
    # "산돌식당": "https://naver.me/xEMZ6QdE",
    "TIP 가가식당": "https://naver.me/GCaFzr8k",
    "E동 레스토랑": "https://naver.me/GRO427Hk",
    "수호식당": "https://naver.me/Gz18OrEt",
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("sandol_logger")
