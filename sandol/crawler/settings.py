
import os

import pytz

# Settings
_PATH = os.path.abspath(os.path.dirname(__file__))  # 프로젝트 절대경로
DEBUG = False  # True 일때 디버그 모드 작동

KST = pytz.timezone('Asia/Seoul')

# BUCKET
BUCKET_NAME: str = 'aws-sandol-bucket'

# Access Token
SANDOL_ACCESS_ID: dict = {
    'MANAGER': "d367f2ec55f41b4207156f4b8fce5ce885b05d8c3b238cf8861c55a9012f6f5895",
    'CONT1': "339b0444bfabbffa0f13508ea7c45b61675b5720234cca8f73cd7421c22de9e546",
    'CONT2': "04eabc8b965bf5ae6cccb122a18521969cc391162e3fd5f61b85efe8bb12e5e98a",
    'CONT3': "def99464e022b38389697fe68d54bbba723d1da291094c19bbf5eaace7b059a997",
    'MINJU': "1ddffbb02b29a6beb212d2f6fe2469523b9a90f260344b9d30677abcd977e1b56c",
    'YURIM': "16b3777b75026553a1807d1f361773e080e6441d30c65ea6e89dd0b84c9b58f071",
    'HAMIN': "c0657ad2b0ade045e546d8abb33f45d85f3c826ce797800e0bf25aac0652bf175c",
    'JDONG': "cbdb6ec7c1427fd603a9c87ee5a1f7d1cc948ca896a2d65f88c770aa742218cef0"
}
# 산돌팀만 접근할 수 있는 컨텐츠에 인증 수단으로 사용 (현재 아이디의 정확한 위치가 기억이 나지 않아.. KEY를 메니저와, CONTRIBUTOR로 명명함.)

RESTAURANT_ACCESS_ID: dict = {
    "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6": "미가식당",
    "380da59920b84d81eb8c444e684a53290021b38f544fe0029f4b38ab347bc44e08": "세미콘식당",
    # "0029ff0cd22a70533cf6b647e5dd36aa13e6981d3f958f953c6c5ef3b879032743": "산돌식당",
    "001": "TIP 가가식당",
    "002": "E동 레스토랑"
}

RESTAURANT_OPEN_PRICE: dict = {
    "미가식당": ["오전 11:00-1:00 / 오후 5:00-6:30", 6000],
    "세미콘식당": ["오전 11:30-1:30 / 오후 5:00-6:00", 6000],
    # "산돌식당": ["오후 12:00-1:00 / 오후 5:30-6:30", 6500],
    "TIP 가가식당": ["오전 11:00-2:00 / 오후 5:00-6:50", 6000],
    "E동 레스토랑": ["오전 11:30-1:50 / 오후 4:50-6:40", 6500]
}
