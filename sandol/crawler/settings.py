import os
import json

##2024-04-04 기나혜
##cafeteria 개발 중에 bucket download 관련 애로사항이 있어
##이전 베타 산돌에 있던 settings 코드를 잠시 긁어왓씁니다..
##추후수정 or 폐기예정

# Settings
_PATH = os.path.abspath(os.path.dirname(__file__))  # 프로젝트 절대경로
DEBUG = False  # True 일때 디버그 모드 작동

# BUCKET
BUCKET_NAME: str = 'aws-sandol-bucket'

# Access Token
SANDOL_ACCESS_ID: dict = {'MANAGER': "d367f2ec55f41b4207156f4b8fce5ce885b05d8c3b238cf8861c55a9012f6f5895",
                          'CONT1': "339b0444bfabbffa0f13508ea7c45b61675b5720234cca8f73cd7421c22de9e546",
                          'CONT2': "04eabc8b965bf5ae6cccb122a18521969cc391162e3fd5f61b85efe8bb12e5e98a",
                          'CONT3': "def99464e022b38389697fe68d54bbba723d1da291094c19bbf5eaace7b059a997",
                          'MINJU': "1ddffbb02b29a6beb212d2f6fe2469523b9a90f260344b9d30677abcd977e1b56c",
                          'YURIM': "16b3777b75026553a1807d1f361773e080e6441d30c65ea6e89dd0b84c9b58f071",
                          'HAMIN': "c0657ad2b0ade045e546d8abb33f45d85f3c826ce797800e0bf25aac0652bf175c",
                          'JDONG' : "cbdb6ec7c1427fd603a9c87ee5a1f7d1cc948ca896a2d65f88c770aa742218cef0"
                          }
# 산돌팀만 접근할 수 있는 컨텐츠에 인증 수단으로 사용 (현재 아이디의 정확한 위치가 기억이 나지 않아.. KEY를 메니저와, CONTRIBUTOR로 명명함.)

RESTAURANT_ACCESS_ID: dict = {"32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6": "미가식당",
                              "380da59920b84d81eb8c444e684a53290021b38f544fe0029f4b38ab347bc44e08": "세미콘식당"
                              }



# RESTAURANT_MENU: str = "restaurant_menu.txt"  # 학식이 저장된 파일 이름 (Bucket)
# LOCAL_RESTAURANT_MENU: str = "/tmp/" + RESTAURANT_MENU  # 람다 서버의 해당 디렉토리에 불러옴
#
# FEEDBACK_FILE: str = "feedback.txt"  # 피드백이 저장된 파일 이름
# LOCAL_FEEDBACK_FILE: str = "/tmp/" + FEEDBACK_FILE  # 람다 서버 tmp 디렉토리에 불러와 실행

# # Urls
# SANDOL_CATEGORY_1: str = "https://github.com/hhhminme/kpu_sandol_team/blob/06916e07fe02d36d3384dfe96c8d2dc4cb300aa7/img/card1.png"  # 인기 메뉴
# SANDOL_CATEGORY_2: str = "https://github.com/hhhminme/kpu_sandol_team/blob/06916e07fe02d36d3384dfe96c8d2dc4cb300aa7/img/card2.png"  # 놀거리
# SANDOL_CATEGORY_3: str = "https://github.com/hhhminme/kpu_sandol_team/blob/06916e07fe02d36d3384dfe96c8d2dc4cb300aa7/img/card3.png"  # 교내 정보
# SANDOL_CATEGORY_4: str = "https://github.com/hhhminme/kpu_sandol_team/blob/main/img/card_other.png"  # 기타 기능
# SANDOL_COVID_IMG: str = "https://raw.githubusercontent.com/hhhminme/kpu_sandol_team/main/img/card_covid.png"  # 코로나
# SANDOL_RSTRNT_FOOD_IMG: str = "https://github.com/hhhminme/kpu_sandol_team/blob/main/img/card_food.png"  # 푸드라운지
# SANDOL_RSTRNT_MIGA_IMG: str = "https://github.com/hhhminme/kpu_sandol_team/blob/main/img/card_miga.png"  # 미가식당
# SANDOL_RSTRNT_MAP: str = "https://raw.githubusercontent.com/hhhminme/kpu_sandol_team/main/img/meal_map.png"  # 식당지도
# SANDOL_LOGO1: str = "https://raw.githubusercontent.com/hhhminme/kpu_sandol_team/main/img/logo1.png"  # 산돌이 로고 (필요시 사용)
# SANDOL_PROFILE1: str = "https://github.com/hhhminme/kpu_sandol_team/blob/main/img/logo_profile1.png"  # 산돌이 프로필 (필요시 사용)
#
#
# # Others
#
