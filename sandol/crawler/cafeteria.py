import os
import json
import datetime as dt

from bucket.common import download_file_from_s3, BUCKET_NAME, FILE_KEY, get_s3_client, upload_file_to_s3
from . import settings


class Restaurant:
    def __init__(self, name, lunch, dinner, location, registration):
        self.registration_time = registration
        self.opening_time = []
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.price_per_person = 0
        self.temp_lunch = []
        self.temp_dinner = []
        self.final_menu = []

        self.rest_info()

    @classmethod
    def by_dict(cls, data):
        """
        주어진 데이터 딕셔너리로부터 Restaurant 객체를 생성합니다.
        """
        registration_time = dt.datetime.fromisoformat(data["registration_time"])
        class_name = f"{data['name']}"
        new_class = type(class_name, (Restaurant,), {})

        return new_class(data["name"], data["lunch_menu"], data["dinner_menu"], data["location"], registration_time)

    @classmethod
    def by_id(cls, id_address):
        """
        식당 별 access id 조회, 식당 이름으로 객체 생성.
        settings. RESTAURANT_ACCESS_ID : {id : name}
        """
        restaurant_name = settings.RESTAURANT_ACCESS_ID.get(id_address)

        if restaurant_name:
            download_path = '/tmp/test.json'  # 임시 경로에 파일 다운로드

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
                    start_time = start_time.split()[0] + ' ' + start_time.split()[1] + ':00'
                elif ':' not in end_time:
                    end_time = end_time + ':00'

                start = dt.datetime.strptime(start_time, '%p %I:%M').time()
                end = dt.datetime.strptime(end_time, '%I:%M').time()

                self.opening_time.append([start.strftime("%p %I:%M"), end.strftime("%I:%M")])

        else:
            raise ValueError(f"레스토랑 '{self.name}'에 대한 정보를 찾을 수 없습니다.")

    def add_menu(self, meal_time, menu):
        """
            *registration
            단일 메뉴 추가 메서드
        """
        if not isinstance(meal_time, str):
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.temp_lunch:
                raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")
            else:
                self.temp_lunch.append(menu)

        elif meal_time.lower() == "dinner":
            if menu in self.temp_dinner:
                raise ValueError("해당 메뉴는 이미 메뉴 목록에 존재합니다.")
            else:
                self.temp_dinner.append(menu)

        else:
            raise ValueError("meal_time should be 'lunch' or 'dinner'.")

        # save temp_menu.json
        self.save_temp_menu()

    def delete_menu(self, meal_time, menu):
        """
            *registration
            단일 메뉴 삭제 메서드
        """
        if not isinstance(meal_time, str):
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.temp_lunch:
                self.temp_lunch.remove(menu)
            else:
                raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        elif meal_time.lower() == "dinner":
            if menu in self.temp_dinner:
                self.temp_dinner.remove(menu)
            else:
                raise ValueError("해당 메뉴는 등록되지 않은 메뉴입니다.")

        else:
            raise ValueError("meal_time should be 'lunch' or 'dinner'.")

        # save temp_menu.json
        self.save_temp_menu()

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

        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(temp_menu, file, ensure_ascii=False, indent=4)

    def load_temp_menu(self):
        """
            *registration
            test.json 파일에서 lunch, dinner 리스트를 불러와 self 인스턴스에 저장
        """
        # only read
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

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
        elif menu_type == "dinner" and self.temp_dinner:
            return self.temp_dinner

    def submit(self):
        """
            temp_menu.json 파일의 "lunch", "dinner" 데이터에 변화가 생길 때
            원본 test.json 파일에 덮어씀, 동시에 self.temp_menu 초기화.
        """
        # TODO(Seokyoung_Hong): S3용으로 수정 필요
        filename = os.path.join('/tmp', 'test.json')

        # read and write
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []
        except FileNotFoundError:
            raise FileNotFoundError(f"{filename} 파일을 찾을 수 없습니다.")

        restaurant_found = False
        for restaurant_data in data:
            if restaurant_data["name"] == self.name:    # 식당 검색
                restaurant_data["lunch_menu"] = self.submit_update_menu("lunch")   # 점심 메뉴 변경 사항 존재 시 submit
                restaurant_data["dinner_menu"] = self.submit_update_menu("dinner")  # 저녁 메뉴 변경 사항 존재 시 submit
                restaurant_data["registration_time"] = dt.datetime.now().isoformat()    # registration time update
                restaurant_data["opening_time"] = self.opening_time                 # opining time update
                restaurant_data["price_per_person"] = self.price_per_person         # 가격 update
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
    download_path = '/tmp/test.json'  # 임시 경로에 파일 다운로드

    download_file_from_s3(BUCKET_NAME, FILE_KEY, download_path)

    with open(download_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 식당 목록 리스트
    restaurants = [Restaurant.by_dict(item) for item in data]

    return restaurants


if __name__ == "__main__":
    # rests = get_meals()
    # print(rests)
    identification = "001"      # 001: TIP 가가식당
    rest = Restaurant.by_id(identification)

    print(rest)
