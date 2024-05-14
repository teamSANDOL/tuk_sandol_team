import os
import json
import settings
    # from sandol.crawler import settings
    # from . import settings : ImportError 발생


class Restaurant:
    def __init__(self, name, lunch, dinner, location):
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.temp_lunch = []
        self.temp_dinner = []
        self.final_menu = []

    @classmethod
    def by_id(cls, id_address):
        # 식당 별 access id 조회, 식당 이름으로 객체 생성.
        # settings. RESTAURANT_ACCESS_ID : {id : name}
        restaurant_name = settings.RESTAURANT_ACCESS_ID.get(id_address)

        if restaurant_name:
            # test.json : {id:"", name: "", lunch : "" ...}
            current_dir = os.path.dirname(__file__)
            filename = os.path.join(current_dir, 'test.json')

            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for restaurant_data in data:
                    # id 검사
                    if restaurant_data["identification"] == id_address:
                        class_name = f"{restaurant_data['name']}"
                        # 클래스 이름을 각 식당명으로 규정
                        new_class = type(class_name, (Restaurant,), {})
                        # 생성된 클래스로 객체를 생성하여 반환
                        return new_class(restaurant_data["name"], restaurant_data["lunch_menu"],
                                         restaurant_data["dinner_menu"], restaurant_data["location"])

        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{id_address}'")

    def add_menu(self, meal_time, menu):        # 단일 메뉴 추가 메서드
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

    def delete_menu(self, meal_time, menu):         # 단일 메뉴 삭제 메서드
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

    def clear_menu(self):       # lunch, dinner, temp all clear
        self.lunch = []
        self.dinner = []
        self.temp_lunch = []
        self.temp_dinner = []

    def save_temp_menu(self):
        """
            temp_menu saving method
            using in add_menu(), delete_menu() method
        """
        # only write
        temp_menu = {"lunch": self.temp_lunch, "dinner": self.temp_dinner}

        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(temp_menu, file, ensure_ascii=False, indent=4)

    def load_temp_menu(self):
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
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, 'test.json')

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
                restaurant_found = True
                break

        if not restaurant_found:
            raise ValueError(f"레스토랑 '{self.name}'가 test.json 파일에 존재하지 않습니다.")

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # 임시 파일 삭제
        temp_menu_path = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        if os.path.exists(temp_menu_path):
            os.remove(temp_menu_path)
        else:
            raise ValueError("temp_menu.json file doesn't exist")

    def __str__(self):
        return f"Restaurant: {self.name}, Lunch: {self.lunch}, Dinner: {self.dinner}, Location: {self.location}"


if __name__ == "__main__":
    identification = "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6"
    rest = Restaurant.by_id(identification)
