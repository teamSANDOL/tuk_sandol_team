"""산돌이에 입점한 식당의 정보를 담는 클래스를 정의하는 모듈입니다.

Restaurant(class): 각 식당의 정보와 점심, 저녁 메뉴를 업데이트하여, 식당의 이름으로 객체를 반환합니다.
get_meals(): s3 버킷에 저장된 data를 json파일로 변환 후 식당의 이름 정보로 식당의 객체를 생성합니다.
"""
import os
import json
import datetime as dt

from bucket.common import download_file_from_s3, BUCKET_NAME, FILE_KEY, upload_file_to_s3
from crawler import settings

DOWNLOAD_PATH = "/tmp/test.json"
UPLOAD_PATH = "/tmp/test.json"


class Restaurant:
    """식당 객체를 생성하는 클래스입니다.

    식당의 전반적 정보를 담아 하나의 식당 객체로 반환하기 위해 사용됩니다.
    식당의 정보는 등록시간, 개점시간, 이름, 메뉴, 위치, 가격을 가집니다.
    Restaurant.by_id() 메서드 호출과 동시에 id와 매칭된 식당의 이름으로 객체가 생성됩니다.

    이 클래스는 식당의 점심메뉴와 저녁메뉴를 삭제, 추가할 수 있습니다.
    따라서 add_menu, delete_menu 메서드를 제공합니다.

    메뉴 정보의 손상을 방지하기 위해 임시 메뉴 정보를 정의합니다.
    모든 메뉴 수정 사항이 종료되면 임시 메뉴 정보를 최종 반환하기 위해 submit 메서드를 사용합니다.

    Attributes:
        registration_time (datetime) : 식당 객체 생성(식당 정보 등록) 시간
        opening_time (list) : 식당의 개점 시간
        name (str) : 식당의 이름
        lunch (list) : 식당의 점심 메뉴 정보
        dinner (list) : 식당의 저녁 메뉴 정보
        location (str) : 식당의 위치 정보(교내/외)
        price_per_person (int) : 식당의 1인분 가격 정보
        temp_lunch (list) : 임시 점심 메뉴 저장 리스트
        temp_dinner (list) : 임시 저녁 메뉴 저장 리스트

    Examples:
    >>> rest1 = Restaurant()
    {
        "identification": "001",
        "name": "TIP 가가식당",
        "registration_time": "2024-05-25T13:47:41.667713",
        "opening_time": [
           [ "AM 11:00", "02:00"],
           ["PM 05:00", "06:50" ]
        ],
        "lunch_menu": [],
        "dinner_menu": [],
        "location": "TIP 지하 1층",
        "price_per_person": 6000
    }
    """
    def __init__(self, name, lunch, dinner, location, registration):
        """Restaurant 객체 초기화

        Args:
            name (str) : 식당의 이름
            lunch (list) : 식당의 점심 메뉴 정보
            dinner (list) : 식당의 저녁 메뉴 정보
            location (str) : 식당의 위치 정보(교내/외)
        """
        self.registration_time = registration
        self.opening_time = []
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.price_per_person = 0
        self.temp_lunch, self.temp_dinner = [], []

        self.rest_info()

    @classmethod
    def by_dict(cls, data):
        """딕셔너리를 Restaurant 객체로 반환합니다.

        변환할 딕셔너리는 다음과 같은 형태입니다.
        {
            "identification": "001",
            "name": "TIP 가가식당",
            "registration_time": "2024-05-25T13:47:41.667713",
            "opening_time": [
                [ "AM 11:00", "02:00"],
                ["PM 05:00", "06:50" ]
            ],
            "lunch_menu": [],
            "dinner_menu": [],
            "location": "TIP 지하 1층",
            "price_per_person": 6000
        }

        딕셔너리 데이터의 "name"을 이름으로 가지는 객체를 생성합니다.

        Args:
            data (dict): 변환할 딕셔너리

        Returns:
            Restaurant: 변환된 Restaurant 객체
        """
        registration_time = dt.datetime.fromisoformat(
            data["registration_time"])
        class_name = f'{data["name"]}'
        new_class = type(class_name, (Restaurant,), {})

        return new_class(data["name"], data["lunch_menu"], data["dinner_menu"],
                         data["location"], registration_time)

    @classmethod
    def by_id(cls, id_address):
        """주어진 ID코드를 조회하여 식당 객체를 생성합니다.

        S3버킷의 데이터를 임시 json 파일(/tmp/test.json)로 다운로드 합니다.
        crawler.settings.py의 ACCESS_ID 딕셔너리를 조회합니다.
        ID정보가 존재한다면 ID의 value인 NAME을 이름으로 가지는
        Restaurant 객체를 생성하여 반환합니다.

        Args:
            id_address (str) : 조회할 ID 코드

        Returns:
            Restaurant: S3버킷 데이터를 변환한 식당 객체

        Raises:
            KeyError: setting 딕셔너리에 존재하는 ID코드가 아닐 때 발생합니다.
        """
        restaurant_name = settings.RESTAURANT_ACCESS_ID.get(id_address)

        if restaurant_name:
            download_file_from_s3(BUCKET_NAME, FILE_KEY, DOWNLOAD_PATH)

            with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

                for restaurant_data in data:
                    if restaurant_data["identification"] == id_address:
                        return cls.by_dict(restaurant_data)
        raise KeyError(f"해당 식당을 찾을 수 없습니다. ID: {id_address}")

    def rest_info(self):
        """각 식당의 불변 정보를 저장합니다.

        crawler.settings.py의 OPNE_PRICE 딕셔너리에서
        식당 이름을 조회하여 식당 정보를 객체에 저장합니다.
        저장하는 정보는 식당 개점 시간(datetime), 가격정보(int) 입니다.

        Raises:
            KeyError: setting 딕셔너리에 존재하는 식당 이름이 아닐 때 발생합니다.
        """
        info = settings.RESTAURANT_OPEN_PRICE

        if self.name in info:
            time_info, self.price_per_person = info[self.name]
            time_slots = time_info.split(" / ")

            self.opening_time = []
            for slot in time_slots:
                if "오전" in slot:
                    slot = slot.replace("오전", "AM ")
                elif "오후" in slot:
                    slot = slot.replace("오후", "PM ")

                start_time, end_time = slot.split("-")
                start_time = start_time.strip().replace("시", ":").replace("분", "")
                end_time = end_time.strip().replace("시", ":").replace("분", "")

                # 분 정보가 없는 경우 :00 추가
                if ':' not in start_time.split()[1]:
                    start_time = start_time.split(
                    )[0] + ' ' + start_time.split()[1] + ":00"
                elif ':' not in end_time:
                    end_time = end_time + ":00"

                start = dt.datetime.strptime(start_time, "%p %I:%M").time()
                end = dt.datetime.strptime(end_time, "%I:%M").time()

                self.opening_time.append(
                    [start.strftime("%p %I:%M"), end.strftime("%I:%M")])

        else:
            raise KeyError(f"레스토랑 {self.name}에 대한 정보를 찾을 수 없습니다.")

    def add_menu(self, meal_time, menu):
        """시간 정보를 토대로 메뉴를 추가합니다.

        시간 정보를 토대로 해당 시간의 임시 메뉴 리스트(temp_시간)에
        메뉴를 추가 후 임시 리스트에 저장합니다.
        기존 리스트에 존재하는 메뉴는 중복 저장하지 않습니다.

        Args:
            meal_time (str): 추가할 메뉴의 시간(점심, 저녁)
            menu (str): 추가할 메뉴

        Raises:
            TypeError: meal_time 값이 "lunch", "dinner"가 아닐 경우 발생합니다.
            ValueError: 추가하려는 메뉴가 객체의 temp_시간 리스트에 이미 존재할 경우 발생합니다.
        """
        if not isinstance(meal_time, str):
            raise TypeError(
                "meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu not in self.temp_lunch:
                self.temp_lunch.append(menu)
                self.save_temp_menu()
            raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")

        if meal_time.lower() == "dinner":
            if menu not in self.temp_dinner:
                self.temp_dinner.append(menu)
                self.save_temp_menu()
            raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")

        raise TypeError("meal_time should be 'lunch' or 'dinner'.")

    def delete_menu(self, meal_time, menu):
        """시간 정보를 토대로 메뉴를 삭제합니다.

        시간 정보를 토대로 해당 시간의 임시 메뉴 리스트(temp_시간)에
        메뉴를 삭제 후 임시 리스트에 저장합니다.
        기존 리스트에 존재하지 않는 메뉴는 삭제 동작을 하지 않습니다.

        Args:
            meal_time (str): 삭제할 메뉴의 시간(점심, 저녁)
            menu (str): 삭제할 메뉴

        Raises:
            TypeError: meal_time 값이 "lunch", "dinner"가 아닐 경우 발생합니다.
            ValueError: 삭제하려는 메뉴가 객체의 temp_시간 리스트에 존재하지 않을 경우 발생합니다.
        """
        if not isinstance(meal_time, str):
            raise TypeError(
                "meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.temp_lunch:
                self.temp_lunch.remove(menu)
                self.save_temp_menu()
            raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        if meal_time.lower() == "dinner":
            if menu in self.temp_dinner:
                self.temp_dinner.remove(menu)
                self.save_temp_menu()
            raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        raise TypeError("meal_time should be 'lunch' or 'dinner'.")

    def clear_menu(self):
        """객체의 메뉴 리스트를 초기화합니다.

        식당 객체의 메뉴 정보와 관련된 모든 인스턴스를 초기화합니다.
        """
        self.lunch = []
        self.dinner = []
        self.temp_lunch = []
        self.temp_dinner = []

    def save_temp_menu(self):
        """임시 메뉴 리스트를 임시 파일을 생성하여 저장합니다.

        객체의 임시 메뉴 리스트(temp.lunch, temp.dinner)를
        json형식으로 임시 파일로 생성 후 디렉터리에 저장한다.

        생성된 json파일은 load_temp_menu에서 임시 메뉴 데이터를 다운로드 할 때 사용된다.
        """
        # only write
        temp_menu = {"lunch": self.temp_lunch, "dinner": self.temp_dinner}

        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(temp_menu, file, ensure_ascii=False, indent=4)

    def load_temp_menu(self):
        """디렉터리에 저장된 임시 메뉴 파일(json)을 다운로드합니다.

        임시 메뉴 파일(이름_temp_menu.json)의 데이터를
        식당 객체의 임시 메뉴 리스트(temp_lunch, temp_dinner)에 저장합니다.
        """
        # only read
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                temp_menu = json.load(file)

                self.temp_lunch = temp_menu.get("lunch", [])
                self.temp_dinner = temp_menu.get("dinner", [])

    def submit_update_menu(self, meal_time):
        """임시 메뉴의 변경 사항이 있을 때 메뉴를 업데이트합니다.

        이 메서드는 submit()메서드의 복잡도 완화를 위해 사욯합니다.
        주어진 meal_time("lunch", "dinner")에 해당하는 임시 메뉴 리스트를 반환합니다.

        Args:
            meal_time (str): 시간 정보("lunch", "dinner")

        Returns:
            list: 식당 객체의 임시 메뉴 리스트(temp_시간)
        """
        if meal_time == "lunch" and self.temp_lunch:
            return self.temp_lunch
        if meal_time == "dinner" and self.temp_dinner:
            return self.temp_dinner

    def submit(self):
        """식당 객체 정보를 S3파일로 업로드합니다.

        S3버킷의 데이터를 다운로드하여 식당을 검색합니다.
        검색한 식당이 존재할 경우, 변경된 식당 정보들을 '/tmp/test.json'파일에 저장 후
        S3버킷에 업로드합니다.

        임시 메뉴 파일인 '이름_temp_menu.json'파일은 디렉터리에서 삭제합니다.

        Raises:
            FileNotFoundError: 디렉터리에서 파일을 찾지 못할 경우 발생합니다.
            ValueError: json파일에 존재하지 않는 식당일 경우 발생합니다.
        """
        download_file_from_s3(BUCKET_NAME, FILE_KEY, DOWNLOAD_PATH)

        # read and write
        try:
            with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{DOWNLOAD_PATH} 파일을 찾을 수 없습니다.") from e

        restaurant_found = False
        for restaurant_data in data:
            if restaurant_data["name"] == self.name:    # 식당 검색
                restaurant_data["lunch_menu"] = self.submit_update_menu(
                    "lunch")   # 점심 메뉴 변경 사항 존재 시 submit
                restaurant_data["dinner_menu"] = self.submit_update_menu(
                    "dinner")  # 저녁 메뉴 변경 사항 존재 시 submit
                restaurant_data["registration_time"] = dt.datetime.now(
                ).isoformat()    # registration time update
                # opining time update
                restaurant_data["opening_time"] = self.opening_time
                restaurant_data["price_per_person"] = self.price_per_person
                restaurant_found = True
                break

        if not restaurant_found:
            raise ValueError(f"레스토랑 {self.name}가 test.json 파일에 존재하지 않습니다.")

        # json data 한꺼번에 test.json으로 덮어씌우기
        with open(DOWNLOAD_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # delete temp_menu.json file
        temp_menu_path = os.path.join(
            "/tmp", f'{self.name}_temp_menu.json')

        if os.path.exists(temp_menu_path):
            os.remove(temp_menu_path)

        upload_file_to_s3(UPLOAD_PATH, BUCKET_NAME, FILE_KEY)

    def __str__(self):
        # print test 시 가시성 완화 목적
        return (f"Restaurant: {self.name}, "
                f"Lunch: {self.lunch}, "
                f"Dinner: {self.dinner}, "
                f"Location: {self.location}, "
                f"Registration_time: {self.registration_time}, "
                f"Opening_time: {self.opening_time}, "
                f"Price: {self.price_per_person}"
                )


async def get_meals() -> list:
    """S3버킷에서 서비스 중인 식당을 객체로 생성 후 리스트로 저장하여 반환합니다.

    S3버킷에서 파일을 다운로드 합니다.
    파일의 각 딕셔너리 데이터를 식당 객체로 생성하여
    식당 목록 리스트에 저장 후 식당 목록 리스트를 반환합니다.

    Returns:
        list : 식당 객체들을 저장한 리스트
    """
    download_file_from_s3(BUCKET_NAME, FILE_KEY, DOWNLOAD_PATH)

    with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 식당 목록 리스트
    restaurants = [Restaurant.by_dict(item) for item in data]

    return restaurants


if __name__ == "__main__":
    ID = "001"      # 001: TIP 가가식당
    rest = Restaurant.by_id(ID)

    print(rest)
