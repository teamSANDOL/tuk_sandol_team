""" ibookdownloader.py에서 다운로드 한 data.xlsx 파일을 사용가능한 정보로 가공하는 모듈이다.
현재 한국공학대학교 TIP, E동 식당의 주간 식당메뉴 정보를 가공, 반환한다.
"""

import json
import os
import math
import datetime as dt
import pandas as pd

from crawler.settings import KST
from bucket.common import download_file_from_s3, BUCKET_NAME, FILE_KEY, upload_file_to_s3


class BookTranslator:
    """
        ibookDownloader.py에서 다운로드한 'data.xlsx'을 토대로
        TIP, E동 식당의 식당 정보를 포함한 객체를 반환한다.
    """
    def __init__(self):
        self.identification = ""
        self.name = ""
        self.opening_time = ""
        self.tip_lunch_menu = []
        self.tip_dinner_menu = []
        self.tip_info = {}
        self.e_lunch_menu = []
        self.e_dinner_menu = []
        self.e_info = {}
        self.location = ""
        self.price_per_person = 0

        # Lambda 환경에서는 /tmp 디렉토리를 사용
        filename = os.path.join('/tmp', 'data.xlsx')

        self.df = pd.read_excel(filename)

        # print(self.df)

    def save_menu(self, restaurant):
        """
            당일 요일 검색
            TIP 식당 메뉴 저장 메서드 tip_save_menu() 호출
            E동 식당 메뉴 저장 메서드 e_save_menu() 호출
        """
        now = dt.datetime.now()  # current time search
        weekday = now.isoweekday()  # 요일 구분

        if restaurant == "TIP":
            self.tip_save_menu(weekday)
        elif restaurant == "E":
            self.e_save_menu(weekday)
        else:
            raise ValueError("[Error] Restaurant isn't exist.")

    def tip_save_menu(self, weekday):
        """
            TIP 가가식당 메뉴 저장
            today_menu() 메서드에서 요일정보 획득
            data.xlsx 파일에서 요일에 해당하는 점심메뉴, 저녁메뉴 추출
        """
        self.tip_lunch_menu = list(self.df.iloc[6:12, weekday])     # data.xlsx file 내 1열 8행~13행
        for menu in self.tip_lunch_menu:
            if menu == '*복수메뉴*':                # *복수메뉴* 글자 제거
                self.tip_lunch_menu.remove(menu)

        self.tip_dinner_menu = list(self.df.iloc[13:19, weekday])   # data.xlsx file 내 1열 15행~20행
        for menu in self.tip_lunch_menu:
            if menu == '*복수메뉴*':
                self.tip_lunch_menu.remove(menu)

    def e_save_menu(self, weekday):
        """
            E동 메뉴 저장
            today_menu() 메서드에서 요일정보 획득
            data.xlsx 파일에서 요일에 해당하는 점심메뉴, 저녁메뉴 추출
        """
        self.e_lunch_menu = list(self.df.iloc[22:29, weekday])  # data.xlsx file 내 1열 24행~30행

        self.e_dinner_menu = list(self.df.iloc[30:37, weekday])  # data.xlsx file 내 1열 32행~38행

    def save_tip_info(self):
        """
        TIP식당의 식당정보 저장 메서드
        """
        self.save_menu("TIP")       # restaurant = "TIP" -> tip_save_menu()
        self.identification = "001"
        self.name = "TIP 가가식당"
        self.opening_time = "오전 11시-2시 / 오후 5시-6:50"
        self.location = "TIP 지하 1층"
        self.price_per_person = 6000

    def save_e_info(self):
        """
        E동 식당의 식당정보 저장 메서드
        """
        self.save_menu("E")         # restaurant = "E" -> e_save_menu()
        self.identification = "002"
        self.name = "E동 레스토랑"
        self.opening_time = "오전 11:30-13:50 / 오후 4:50-18:40"
        self.location = "E동 1층"
        self.price_per_person = 6500

    def submit_tip_info(self):
        """
            save_tip_info 로 팁지 정보 저장
            tip_info {} 로 json 파일 형식으로 저장
            test.json 파일에 덮어쓰기 -> 이미 식당 정보가 존재한다면 lunch, dinner 메뉴만 덮어쓰기
            NaN(엑셀파일 기준 빈칸) 값 제거 후 test.json 저장
        """
        self.save_tip_info()

        self.tip_info = {
            "identification": self.identification,
            "name": self.name,
            "registration_time": dt.datetime.now(tz=KST).isoformat(),
            "opening_time": self.opening_time,
            "lunch_menu": self.tip_lunch_menu,
            "dinner_menu": self.tip_dinner_menu,
            "location": self.location,
            "price_per_person": self.price_per_person
        }

        # S3에서 파일 다운로드
        download_path = '/tmp/test.json'
        try:
            download_file_from_s3(BUCKET_NAME, FILE_KEY, download_path)
            with open(download_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
        except FileNotFoundError:
            data = []
        except json.decoder.JSONDecodeError:
            data = []

        restaurant_found = False
        for restaurant_data in data:
            if restaurant_data.get("name") == self.name:  # 식당 검색
                restaurant_data["lunch_menu"] = self.tip_lunch_menu
                restaurant_data["dinner_menu"] = self.tip_dinner_menu
                restaurant_found = True
                break

        if not restaurant_found:
            data.append(self.tip_info)

        for restaurant in data:
            for key, value in restaurant.items():
                if isinstance(value, list):
                    restaurant[key] = [item for item in value if not (isinstance(item, float)
                                                                      and math.isnan(item))]

        # 임시 파일에 데이터 저장
        with open(download_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # S3에 업로드
        upload_file_to_s3(download_path, BUCKET_NAME, FILE_KEY)
        print(f"File {FILE_KEY} uploaded to S3 bucket {BUCKET_NAME}")

    def submit_e_info(self):
        """
            save_e_info 로 E동 정보 저장
            e_info {} 로 json 파일 형식으로 저장
            test.json 파일에 덮어쓰기 -> 이미 식당 정보가 존재한다면 lunch, dinner 메뉴만 덮어쓰기
            NaN(엑셀파일 기준 빈칸) 값 제거 후 test.json 저장
        """
        self.save_e_info()

        self.e_info = {
            "identification": self.identification,
            "name": self.name,
            "registration_time": dt.datetime.now(tz=KST).isoformat(),
            "opening_time": self.opening_time,
            "lunch_menu": self.e_lunch_menu,
            "dinner_menu": self.e_dinner_menu,
            "location": self.location,
            "price_per_person": self.price_per_person
        }

        # S3에서 파일 다운로드
        download_path = '/tmp/test.json'
        try:
            download_file_from_s3(BUCKET_NAME, FILE_KEY, download_path)
            with open(download_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
        except FileNotFoundError:
            data = []
        except json.decoder.JSONDecodeError:
            data = []

        restaurant_found = False
        for restaurant_data in data:
            if restaurant_data["name"] == self.name:  # 식당 검색
                restaurant_data["lunch_menu"] = self.e_lunch_menu
                restaurant_data["dinner_menu"] = self.e_dinner_menu
                restaurant_found = True
                break

        if not restaurant_found:
            data.append(self.e_info)

        for restaurant in data:
            for key, value in restaurant.items():
                if isinstance(value, list):
                    restaurant[key] = [item for item in value if not (isinstance(item, float)
                                                                      and math.isnan(item))]

        # 임시 파일에 데이터 저장
        with open(download_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # S3에 업로드
        upload_file_to_s3(download_path, BUCKET_NAME, FILE_KEY)
        print(f"File {FILE_KEY} uploaded to S3 bucket {BUCKET_NAME}")


if __name__ == "__main__":
    ibook = BookTranslator()

    ibook.submit_tip_info()     # TIP 가가식당 정보 test.json에 저장
    ibook.submit_e_info()       # E동 레스토랑 정보 test.json에 저장
