"""산돌이에 입점한 식당의 정보를 담는 클래스를 정의하는 모듈입니다.

Restaurant(class): 각 식당의 정보와 점심, 저녁 메뉴를 업데이트하여, 식당의 이름으로 객체를 반환합니다.
get_meals(): json파일을 열어 식당의 객체를 생성합니다.
"""

import os
import json
import datetime as dt

from api_server.settings import logger
from crawler import settings

BUCKET_NAME = "sandol-bucket"
FILE_KEY = "test.json"

DOWNLOAD_PATH = f"{settings._PATH}/data/test.json"


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

    def __init__(
        self,
        name,
        lunch,
        dinner,
        location,
        registration,
        opening_time,
        price_per_person,
    ):
        """Restaurant 객체 초기화 메서드입니다.

        Args:
            name (str): 식당의 이름
            lunch (list): 식당의 점심 메뉴 정보
            dinner (list): 식당의 저녁 메뉴 정보
            location (str): 식당의 위치 정보(교내/외)
            registration (datetime): 식당 객체 생성(식당 정보 등록) 시간
            opening_time (list[list[str]]): 식당의 개점 시간
            price_per_person (int, optional): 식당의 1인분 가격 정보
        """
        self.registration_time = registration
        self.opening_time = opening_time
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.price_per_person = price_per_person
        self.temp_lunch, self.temp_dinner = [], []

    @classmethod
    def by_dict(cls, data):
        """딕셔너리를 Restaurant 객체로 반환합니다.

        변환할 딕셔너리는 다음과 같은 형태입니다.
        {
            "identification": "001",
            "name": "TIP 가가식당",
            "registration_time": "2024-05-25T13:47:41.667713",
            "opening_time": [
                [(11,0), (14,0)],
                [(17,0), (18,50)]
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
        logger.debug("딕셔너리에서 Restaurant 객체 생성: %s", data["name"])
        registration_time = dt.datetime.fromisoformat(data["registration_time"])
        class_name = f'{data["name"]}'
        new_class = type(class_name, (Restaurant,), {})

        return new_class(
            data["name"],
            data["lunch_menu"],
            data["dinner_menu"],
            data["location"],
            registration_time,
            data["opening_time"],
            data["price_per_person"],
        )

    @classmethod
    def by_id(cls, id_address):
        """주어진 ID코드를 조회하여 식당 객체를 생성합니다.

        crawler.settings.py의 ACCESS_ID 딕셔너리를 조회합니다.
        ID정보가 존재한다면 ID의 value인 NAME을 이름으로 가지는
        Restaurant 객체를 생성하여 반환합니다.

        Args:
            id_address (str) : 조회할 ID 코드

        Returns:
            Restaurant: 파일 내용을 변환한 식당 객체

        Raises:
            KeyError: setting 딕셔너리에 존재하는 ID코드가 아닐 때 발생합니다.
        """
        logger.info("ID로 Restaurant 객체 조회: ID=%s", id_address)
        with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        for restaurant_data in data:
            if restaurant_data["identification"] == id_address:
                logger.debug("ID로 식당 찾음: %s", restaurant_data["name"])
                return cls.by_dict(restaurant_data)
        logger.warning("해당 ID로 식당을 찾을 수 없음: ID=%s", id_address)
        raise KeyError(f"해당 식당을 찾을 수 없습니다. ID: {id_address}")

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
        logger.info(
            "메뉴 추가 요청: name=%s, meal_time=%s, menu=%s", self.name, meal_time, menu
        )
        if not isinstance(meal_time, str):
            logger.error("meal_time은 문자열이어야 합니다.")
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu not in self.temp_lunch:
                self.temp_lunch.append(menu)
                self.save_temp_menu()
                logger.debug("점심 메뉴 추가: %s", menu)
            logger.warning("점심 메뉴 중복 추가 시도: %s", menu)
            raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")

        if meal_time.lower() == "dinner":
            if menu not in self.temp_dinner:
                self.temp_dinner.append(menu)
                self.save_temp_menu()
                logger.debug("저녁 메뉴 추가: %s", menu)
            logger.warning("저녁 메뉴 중복 추가 시도: %s", menu)
            raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")

        logger.error("meal_time이 유효하지 않음: %s", meal_time)
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
        logger.info(
            "메뉴 삭제 요청: name=%s, meal_time=%s, menu=%s", self.name, meal_time, menu
        )
        if not isinstance(meal_time, str):
            logger.error("meal_time은 문자열이어야 합니다.")
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.temp_lunch:
                self.temp_lunch.remove(menu)
                self.save_temp_menu()
                logger.debug("점심 메뉴 삭제: %s", menu)
            logger.warning("삭제하려는 점심 메뉴가 존재하지 않음: %s", menu)
            raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        if meal_time.lower() == "dinner":
            if menu in self.temp_dinner:
                self.temp_dinner.remove(menu)
                self.save_temp_menu()
                logger.debug("저녁 메뉴 삭제: %s", menu)
            logger.warning("삭제하려는 저녁 메뉴가 존재하지 않음: %s", menu)
            raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        logger.error("meal_time이 유효하지 않음: %s", meal_time)
        raise TypeError("meal_time should be 'lunch' or 'dinner'.")

    def clear_menu(self):
        """객체의 메뉴 리스트를 초기화합니다.

        식당 객체의 메뉴 정보와 관련된 모든 인스턴스를 초기화합니다.
        """
        logger.info("모든 메뉴 초기화: name=%s", self.name)
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
        logger.debug("임시 메뉴 저장 요청: name=%s", self.name)
        temp_menu = {"lunch": self.temp_lunch, "dinner": self.temp_dinner}
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f"{self.name}_temp_menu.json")

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(temp_menu, file, ensure_ascii=False, indent=4)
        logger.info("임시 메뉴 저장 완료: file=%s", filename)

    def load_temp_menu(self):
        """디렉터리에 저장된 임시 메뉴 파일(json)을 다운로드합니다.

        임시 메뉴 파일(이름_temp_menu.json)의 데이터를
        식당 객체의 임시 메뉴 리스트(temp_lunch, temp_dinner)에 저장합니다.
        """
        logger.debug("임시 메뉴 로드 요청: name=%s", self.name)
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f"{self.name}_temp_menu.json")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                temp_menu = json.load(file)

                self.temp_lunch = temp_menu.get("lunch", [])
                self.temp_dinner = temp_menu.get("dinner", [])
            logger.info("임시 메뉴 로드 완료: file=%s", filename)
        else:
            logger.warning("임시 메뉴 파일이 존재하지 않음: file=%s", filename)

    def submit_update_menu(self, meal_time):
        """임시 메뉴의 변경 사항이 있을 때 메뉴를 업데이트합니다.

        이 메서드는 submit()메서드의 복잡도 완화를 위해 사욯합니다.
        주어진 meal_time("lunch", "dinner")에 해당하는 임시 메뉴 리스트를 반환합니다.

        Args:
            meal_time (str): 시간 정보("lunch", "dinner")

        Returns:
            list: 식당 객체의 임시 메뉴 리스트(temp_시간)
        """
        logger.info(
            "임시 메뉴 업데이트 요청: name=%s, meal_time=%s", self.name, meal_time
        )
        if meal_time == "lunch" and self.temp_lunch:
            logger.debug("점심 메뉴 업데이트: %s", self.temp_lunch)
            return self.temp_lunch
        if meal_time == "dinner" and self.temp_dinner:
            logger.debug("저녁 메뉴 업데이트: %s", self.temp_dinner)
            return self.temp_dinner
        logger.debug("업데이트할 메뉴가 없음: meal_time=%s", meal_time)

    def submit(self):
        """식당 객체 정보를 파일로 저장합니다.

        메뉴가 저장된 파일을 열어 식당을 검색합니다.
        검색한 식당이 존재할 경우, 변경된 식당 정보들을 json 파일에 저장 후
        업로드합니다.

        임시 메뉴 파일인 '이름_temp_menu.json'파일은 디렉터리에서 삭제합니다.

        Raises:
            FileNotFoundError: 디렉터리에서 파일을 찾지 못할 경우 발생합니다.
            ValueError: json파일에 존재하지 않는 식당일 경우 발생합니다.
        """
        # read and write
        try:
            with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []
            logger.error("JSON 디코딩 오류 발생: file=%s", DOWNLOAD_PATH)
        except FileNotFoundError as e:
            logger.error("파일을 찾을 수 없음: file=%s", DOWNLOAD_PATH)
            raise FileNotFoundError(f"{DOWNLOAD_PATH} 파일을 찾을 수 없습니다.") from e

        restaurant_found = False
        for restaurant_data in data:
            if restaurant_data["name"] == self.name:
                restaurant_data["lunch_menu"] = self.submit_update_menu("lunch")
                restaurant_data["dinner_menu"] = self.submit_update_menu("dinner")
                restaurant_data["registration_time"] = dt.datetime.now().isoformat()
                restaurant_data["opening_time"] = self.opening_time
                restaurant_data["price_per_person"] = self.price_per_person
                restaurant_found = True
                logger.debug("식당 정보 업데이트 완료: %s", self.name)
                break

        if not restaurant_found:
            logger.error("제출하려는 식당을 찾을 수 없음: name=%s", self.name)
            raise ValueError(
                f"레스토랑 {self.name}가 test.json 파일에 존재하지 않습니다."
            )

        with open(DOWNLOAD_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logger.info("식당 정보 저장 완료: name=%s, file=%s", self.name, DOWNLOAD_PATH)

        temp_menu_path = os.path.join(
            os.path.dirname(__file__), f"{self.name}_temp_menu.json"
        )

        if os.path.exists(temp_menu_path):
            os.remove(temp_menu_path)
            logger.info("임시 메뉴 파일 삭제 완료: file=%s", temp_menu_path)

    @classmethod
    def init_restaurant(
        cls,
        identification: str,
        name: str,
        opening_time: list,
        location: str,
        price_per_person: int,
        varification_key: str,
    ):
        """test.json에 새로운 식당을 추가합니다."""
        logger.info(
            "새로운 식당 초기화 요청: name=%s, identification=%s", name, identification
        )
        try:
            with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
            logger.warning("등록된 데이터 파일을 찾을 수 없음: file=%s", DOWNLOAD_PATH)

        new_restaurant = {
            "identification": identification,
            "name": name,
            "registration_time": dt.datetime.now().isoformat(),
            "opening_time": opening_time,
            "lunch_menu": [],
            "dinner_menu": [],
            "location": location,
            "price_per_person": price_per_person,
            "varification_key": varification_key,
        }

        # 중복 체크
        for restaurant in data:
            if restaurant["name"] == name:
                logger.error("동일한 이름의 식당이 이미 존재: name=%s", name)
                raise ValueError("동일한 이름의 식당이 이미 존재합니다.")
            if restaurant["identification"] == identification:
                logger.error(
                    "동일한 식당 ID가 이미 존재: identification=%s", identification
                )
                raise ValueError("동일한 식당 ID가 이미 존재합니다.")

        data.append(new_restaurant)

        # 데이터 저장
        with open(DOWNLOAD_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logger.info("새로운 식당 초기화 완료: name=%s, file=%s", name, DOWNLOAD_PATH)

        # restaurant_id.json 업데이트
        RESTAURANT_ACCESS_ID = cls.load_restaurant_ids()
        RESTAURANT_ACCESS_ID[identification] = name
        cls.save_restaurant_ids(RESTAURANT_ACCESS_ID)
        logger.debug(
            "restaurant_id.json 업데이트 완료: name=%s, identification=%s",
            name,
            identification,
        )

    def __str__(self):
        """명령어 print test시 가시성을 완화합니다."""
        return (
            f"Restaurant: {self.name}, "
            f"Lunch: {self.lunch}, "
            f"Dinner: {self.dinner}, "
            f"Location: {self.location}, "
            f"Registration_time: {self.registration_time}, "
            f"Opening_time: {self.opening_time}, "
            f"Price: {self.price_per_person}"
        )

    @classmethod
    def load_pending_restaurants(cls):
        """등록 대기 중인 식당 목록을 로드합니다."""
        try:
            with open(
                f"{settings._PATH}/data/restaurant_register.json", "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning(
                "등록 대기 중인 식당 파일을 찾을 수 없음: file=%s",
                "restaurant_register.json",
            )
            data = []
        return data

    @classmethod
    def save_pending_restaurants(cls, data):
        """등록 대기 중인 식당 목록을 저장합니다."""
        with open(
            f"{settings._PATH}/data/restaurant_register.json", "w", encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_restaurant_ids(cls):
        """식당 ID 정보를 로드합니다."""
        with open(
            f"{settings._PATH}/data/restaurant_id.json", "r", encoding="utf-8"
        ) as f:
            return json.load(f)

    @classmethod
    def save_restaurant_ids(cls, data):
        """식당 ID 정보를 저장합니다."""
        with open(
            f"{settings._PATH}/data/restaurant_id.json", "w", encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def register_new_restaurant(cls, temp_data):
        """새로운 식당을 등록합니다."""
        logger.info(
            "새로운 식당 등록 요청: name=%s, identification=%s",
            temp_data["name"],
            temp_data["identification"],
        )

        # 기존 데이터 로드
        data = cls.load_pending_restaurants()
        logger.debug("현재 대기 중인 식당 데이터 로드 완료: count=%d", len(data))

        # 중복 확인
        for restaurant in data:
            if restaurant["name"] == temp_data["name"]:
                logger.error(
                    "동일한 이름의 식당이 이미 등록 대기 중: name=%s", temp_data["name"]
                )
                raise ValueError("동일한 이름의 식당이 이미 등록 대기 중입니다.")
            if restaurant["identification"] == temp_data["identification"]:
                logger.error(
                    "동일한 식당 ID가 이미 등록 대기 중: identification=%s",
                    temp_data["identification"],
                )
                raise ValueError("동일한 식당 ID가 이미 등록 대기 중입니다.")

        # 신규 식당 추가
        data.append(temp_data)
        cls.save_pending_restaurants(data)
        logger.info(
            "신규 식당 등록 성공: name=%s, identification=%s",
            temp_data["name"],
            temp_data["identification"],
        )

        # restaurant_id.json 업데이트
        RESTAURANT_ACCESS_ID = cls.load_restaurant_ids()
        RESTAURANT_ACCESS_ID[temp_data["identification"]] = temp_data["name"]
        cls.save_restaurant_ids(RESTAURANT_ACCESS_ID)
        logger.debug(
            "restaurant_id.json 업데이트 완료: name=%s, identification=%s",
            temp_data["name"],
            temp_data["identification"],
        )

    @classmethod
    def approve_restaurant(cls, identification, location):
        """식당 등록을 승인합니다."""
        logger.info(
            "식당 등록 승인 요청: identification=%s, location=%s",
            identification,
            location,
        )

        data = cls.load_pending_restaurants()
        logger.debug("현재 대기 중인 식당 데이터 로드 완료: count=%d", len(data))

        restaurant_data_list = list(
            filter(lambda x: x["identification"] == identification, data)
        )

        if not restaurant_data_list:
            logger.error(
                "등록 대기 중인 식당을 찾을 수 없음: identification=%s", identification
            )
            raise ValueError("등록 대기 중인 식당을 찾을 수 없습니다.")

        restaurant_data = restaurant_data_list[0]
        logger.debug(
            "승인 대상 식당 데이터 확인: name=%s, identification=%s",
            restaurant_data["name"],
            restaurant_data["identification"],
        )

        name = restaurant_data["name"]
        price_per_person = restaurant_data["price_per_person"]
        opening_time = restaurant_data["opening_time"]
        varification_key = restaurant_data["varification_key"]

        # 새로운 식당 등록
        cls.init_restaurant(
            identification,
            name,
            opening_time,
            location,
            price_per_person,
            varification_key,
        )
        logger.info(
            "식당 등록 승인 및 초기화 완료: name=%s, identification=%s",
            name,
            identification,
        )

        # 대기 목록에서 제거
        new_restaurant_data = list(
            filter(lambda x: x["identification"] != identification, data)
        )
        cls.save_pending_restaurants(new_restaurant_data)
        logger.debug(
            "등록 대기 목록 업데이트 완료: identification=%s 제거됨", identification
        )

    @classmethod
    def decline_restaurant(cls, identification):
        """식당 등록을 거절합니다."""
        logger.info("식당 등록 거절 요청: identification=%s", identification)
        data = cls.load_pending_restaurants()
        logger.debug("현재 대기 중인 식당 데이터 로드 완료: count=%d", len(data))

        restaurant_data = list(
            filter(lambda x: x["identification"] != identification, data)
        )
        if len(restaurant_data) < len(data):
            logger.info("식당 등록 거절 완료: identification=%s", identification)
        else:
            logger.warning(
                "등록 대기 목록에서 식당을 찾지 못함: identification=%s", identification
            )

        cls.save_pending_restaurants(restaurant_data)
        logger.debug(
            "등록 대기 목록 업데이트 완료: identification=%s 제거됨", identification
        )

    @staticmethod
    def change_identification(varification_key, new_identification):
        """식당의 카카오톡 ID를 변경합니다.

        varification_key에 해당하는 식당의 identification을 new_identification으로 변경합니다.
        이를통해 기존 식당을 유지한 채로, 식당을 관리하는 계정 ID를 변경할 수 있습니다.

        Args:
            varification_key (str): 변경할 식당의 varification_key
            new_identification (str): 변경할 식당의 identification

        Raises:
            FileNotFoundError: 등록된 식당이 없을 경우 발생합니다.
            ValueError: 변경할 식당을 찾을 수 없을 경우 발생합니다.
        """
        logger.info(
            "식당 ID 변경 요청: varification_key=%s, new_identification=%s",
            varification_key,
            new_identification,
        )
        try:
            with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as error:
            logger.error("등록된 식당 파일을 찾을 수 없음: file=%s", DOWNLOAD_PATH)
            raise FileNotFoundError("등록된 식당이 없습니다.") from error

        for restaurant in data:
            if restaurant["varification_key"] == varification_key:
                logger.debug(
                    "varification_key 일치하는 식당 찾음: name=%s", restaurant["name"]
                )
                old_identification = restaurant["identification"]
                restaurant["identification"] = new_identification
                break
        else:
            logger.warning(
                "varification_key와 일치하는 식당을 찾을 수 없음: varification_key=%s",
                varification_key,
            )
            raise ValueError("식당을 찾을 수 없습니다.")

        RESTAURANT_ACCESS_ID = Restaurant.load_restaurant_ids()
        RESTAURANT_ACCESS_ID[new_identification] = restaurant["name"]
        try:
            del RESTAURANT_ACCESS_ID[old_identification]
        except KeyError:
            logger.warning(
                "기존 ID를 restaurant_id.json에서 찾을 수 없음: old_identification=%s",
                old_identification,
            )

        Restaurant.save_restaurant_ids(RESTAURANT_ACCESS_ID)
        logger.info(
            "restaurant_id.json 업데이트 완료: new_identification=%s",
            new_identification,
        )

        with open(DOWNLOAD_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logger.info(
            "식당 ID 변경 및 데이터 저장 완료: new_identification=%s",
            new_identification,
        )

    @staticmethod
    def opening_time_str(opening_time: list) -> str:
        """식당의 개점 시간을 문자열로 변환합니다.

        Args:
            opening_time (list): 식당의 개점 시간 정보

        Returns:
            str: 변환된 개점 시간 문자열
        """

        def format_time(hour, minute):
            period = "오후" if hour >= 12 else "오전"
            hour = hour if hour <= 12 else hour - 12
            return f"{period} {hour:02}:{minute:02}"

        start = format_time(*opening_time[0])
        end = format_time(*opening_time[1])
        return f"{start} - {end}"

    @property
    def lunch_time(self):
        """식당의 점심 시간을 반환합니다."""
        return self.opening_time_str(self.opening_time[0])

    @property
    def dinner_time(self):
        """식당의 저녁 시간을 반환합니다."""
        return self.opening_time_str(self.opening_time[1])


async def get_meals() -> list:
    """JSON 파일을 열어 내용을 객체로 생성 후 리스트로 저장하여 반환합니다.

    파일의 각 딕셔너리 데이터를 식당 객체로 생성하여
    식당 목록 리스트에 저장 후 식당 목록 리스트를 반환합니다.

    Returns:
        list : 식당 객체들을 저장한 리스트
    """
    logger.info("식당 목록 로드 요청")
    with open(DOWNLOAD_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    restaurants = [Restaurant.by_dict(item) for item in data]
    logger.debug("식당 목록 로드 완료: count=%d", len(restaurants))
    return restaurants


if __name__ == "__main__":
    ID = "001"  # 001: TIP 가가식당
    rest = Restaurant.by_id(ID)

    print(rest)
