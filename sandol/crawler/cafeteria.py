"""
Restaurant(class): 산돌이에 입점한 식당의 정보를 담는 클래스를 정의하는 모듈입니다.
get_meals(): s3 버킷에 저장된 data를 json파일로 변환 후 식당의 이름 정보로 식당의 객체를 생성합니다.
"""
import os
import json
import datetime as dt

from bucket.common import download_file_from_s3, BUCKET_NAME, FILE_KEY, upload_file_to_s3
from crawler import settings


class Restaurant:
    """식당 정보를 담고 메뉴 정보를 추가, 수정, 등록, 삭제하기 위해 사용됩니다.
        Restaurant.by_id() 메서드 호출과 동시에 id와 매칭된 식당의 이름으로 객체가 생성됩니다.

        메뉴 정보 수정 용 메서드: add_menu, delete_menu, clear_menu
        식당 정보 반환 용 메서드: submit
    """
    def __init__(self, name, lunch, dinner, location, registration):
        self.registration_time = registration       # 점주가 식당 메뉴를 등록한 시간(datetime)
        self.opening_time = []                      # 식당 개점 시간(datetime)
        self.name = name                            # 식당 이름 정보(str)
        self.lunch = lunch                          # 식당 점심 메뉴 정보(list)
        self.dinner = dinner                        # 식당 저녁 메뉴 정보(list)
        self.location = location                    # 식당 위치 정보 - 교내/외(str)
        self.price_per_person = 0                   # 식당 1인분 가격 정보
        self.temp_lunch = []                        # 식당 점심 메뉴 수정 용 임시 메뉴 저장 리스트
        self.temp_dinner = []                       # 식당 저녁 메뉴 수정 용 임시 메뉴 저장 리스트

        self.rest_info()

    @classmethod
    def by_dict(cls, data):
        """
        주어진 데이터 딕셔너리로부터 Restaurant 객체를 생성합니다.
        get_meals()에서 사용합니다.
        """
        registration_time = dt.datetime.fromisoformat(
            data["registration_time"])
        class_name = f"{data['name']}"
        new_class = type(class_name, (Restaurant,), {})

        return new_class(data["name"], data["lunch_menu"], data["dinner_menu"],
                         data["location"], registration_time)

    @classmethod
    def by_id(cls, id_address, donwload: bool = True):
        """
        식당 별 access id 조회, 식당 이름으로 객체 생성.
        settings. RESTAURANT_ACCESS_ID : {id : name}
        """
        restaurant_name = settings.RESTAURANT_ACCESS_ID.get(id_address)

        if restaurant_name:
            download_path = '/tmp/test.json'  # 임시 경로에 파일 다운로드

            if donwload:
                download_file_from_s3(BUCKET_NAME, FILE_KEY, download_path)

            with open(download_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for restaurant_data in data:
                    # id 검사
                    if restaurant_data["identification"] == id_address:
                        return cls.by_dict(restaurant_data)
        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{id_address}'")

    def rest_info(self):
        """
            *registration
            각 식당의 개점, 폐점 시간 정보, 1인분 가격 정보 저장 메서드
        """
        info = {
            "미가식당": ["오전 11:00-1:00 / 오후 5:00-6:30", 6000],
            "세미콘식당": ["오전 11:30-1:30 / 오후 5:00-6:00", 6000],
            "산돌식당": ["오후 12:00-1:00 / 오후 5:30-6:30", 6500],
            "TIP 가가식당": ["오전 11:00-2:00 / 오후 5:00-6:50", 6000],
            "E동 레스토랑": ["오전 11:30-1:50 / 오후 4:50-6:40", 6500]
        }

        if self.name in info:
            time_info, self.price_per_person = info[self.name]
            time_slots = time_info.split(" / ")

            self.opening_time = []
            for slot in time_slots:
                if '오전' in slot:
                    slot = slot.replace('오전', 'AM ')
                elif '오후' in slot:
                    slot = slot.replace('오후', 'PM ')

                start_time, end_time = slot.split('-')
                start_time = start_time.strip().replace('시', ':').replace('분', '')
                end_time = end_time.strip().replace('시', ':').replace('분', '')

                # 분 정보가 없는 경우 :00 추가
                if ':' not in start_time.split()[1]:
                    start_time = start_time.split(
                    )[0] + ' ' + start_time.split()[1] + ':00'
                elif ':' not in end_time:
                    end_time = end_time + ':00'

                start = dt.datetime.strptime(start_time, '%p %I:%M').time()
                end = dt.datetime.strptime(end_time, '%I:%M').time()

                self.opening_time.append(
                    [start.strftime("%p %I:%M"), end.strftime("%I:%M")])

        else:
            raise ValueError(f"레스토랑 '{self.name}'에 대한 정보를 찾을 수 없습니다.")

    def add_menu(self, meal_time, menu):
        """
            *registration
            단일 메뉴 추가 메서드
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

        raise ValueError("meal_time should be 'lunch' or 'dinner'.")

    def delete_menu(self, meal_time, menu):
        """
            *registration
            단일 메뉴 삭제 메서드
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

        raise ValueError("meal_time should be 'lunch' or 'dinner'.")

    def clear_menu(self):
        """
            *registration
            lunch, dinner, temp all clear
        """
        self.lunch = []
        self.dinner = []
        self.temp_lunch = []
        self.temp_dinner = []

    def save_temp_menu(self):
        """
            *registration
            temp_menu 저장 메서드
            using in add_menu(), delete_menu() method
            self 인스턴스에 들어있는 메뉴 리스트를 json 파일에 덮어씌우기
        """
        # only write
        temp_menu = {"lunch": self.temp_lunch, "dinner": self.temp_dinner}

        filename = os.path.join("/tmp", f'{self.name}_temp_menu.json')

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(temp_menu, file, ensure_ascii=False, indent=4)

    def load_temp_menu(self):
        """
            *registration
            test.json 파일에서 lunch, dinner 리스트를 불러와 self 인스턴스에 저장
        """
        # only read
        filename = os.path.join("/tmp", f'{self.name}_temp_menu.json')

        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                temp_menu = json.load(file)

                self.temp_lunch = temp_menu.get('lunch', [])
                self.temp_dinner = temp_menu.get('dinner', [])

    def submit_update_menu(self, menu_type):
        """
            submit(self)에서 사용. (복잡도 완화 목적)
            :param menu_type: 업데이트할 메뉴 시간정보 ("lunch" 또는 "dinner").
            example: self.update_menu(restaurant_data, "lunch")
        """
        if menu_type == "lunch" and self.temp_lunch:
            return self.temp_lunch
        if menu_type == "dinner" and self.temp_dinner:
            return self.temp_dinner

    def submit(self):
        """
            temp_menu.json 파일의 "lunch", "dinner" 데이터에 변화가 생길 때
            원본 test.json 파일에 덮어씀, 동시에 self.temp_menu 초기화.
        """
        filename = os.path.join('/tmp', 'test.json')

        # read and write
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{filename} 파일을 찾을 수 없습니다.") from e

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
                # 가격 update
                restaurant_data["price_per_person"] = self.price_per_person
                restaurant_found = True
                break

        if not restaurant_found:
            raise ValueError(f"레스토랑 '{self.name}'가 test.json 파일에 존재하지 않습니다.")

        with open(filename, 'w', encoding='utf-8') as file:
            # json data 한꺼번에 test.json으로 덮어씌우기
            json.dump(data, file, ensure_ascii=False, indent=4)

        # 임시 파일 삭제
        temp_menu_path = os.path.join(
            "/tmp", f'{self.name}_temp_menu.json')

        if os.path.exists(temp_menu_path):
            os.remove(temp_menu_path)
        else:
            raise ValueError("temp_menu.json file doesn't exist")

        upload_path = '/tmp/test.json'  # 임시 경로에 파일 업로드
        upload_file_to_s3(upload_path, BUCKET_NAME, FILE_KEY, )

    def __str__(self):
        """
            print() test 시 출력 메세지 가시성 완화 목적
        """
        return (f"Restaurant: {self.name}, Lunch: {self.lunch}, Dinner: {self.dinner}, "
                f"Location: {self.location}, Registration_time: {self.registration_time}, "
                f"Opening_time: {self.opening_time}, Price: {self.price_per_person}")


async def get_meals() -> list:
    """
        bucket에서 서비스중인 식당 목록을 불러옴
        각 식당의 identification 코드를 조회하여 인증
        인증된 식당일 경우 식당의 이름으로 Restaurant 객체 반환
    """
    download_path = '/tmp/test.json'  # 임시 경로에 파일 다운로드

    download_file_from_s3(BUCKET_NAME, FILE_KEY, download_path)

    with open(download_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 식당 목록 리스트
    restaurants = [Restaurant.by_dict(item) for item in data]

    return restaurants


if __name__ == "__main__":
    ID = "001"      # 001: TIP 가가식당
    rest = Restaurant.by_id(ID)

    print(rest)
