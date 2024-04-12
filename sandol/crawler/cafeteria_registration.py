import os
import json
import settings


class Restaurant:
    def __init__(self, name, lunch, dinner, location):
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.id = ""
        self.temp_menu = {"lunch": lunch, "dinner": dinner}
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

    def add_menu(self, meal_time, menu):         # 단일 메뉴 추가 메서드
        if not isinstance(meal_time, str):
            raise TypeError(
                "meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.lunch:
                print("해당 메뉴는 이미 메뉴 목록에 존재 합니다.")
            else:
                self.lunch.append(menu)
        elif meal_time.lower() == "dinner":
            if menu in self.dinner:
                print("해당 메뉴는 이미 메뉴 목록에 존재 합니다.")
            else:
                self.dinner.append(menu)
        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")

        # save temp_menu.json
        self.save_temp_menu()

    def delete_menu(self, meal_time, menu):         # 단일 메뉴 삭제 메서드
        if not isinstance(meal_time, str):
            raise TypeError(
                "meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            if menu in self.lunch:
                self.lunch.remove(menu)
            else:
                print("해당 메뉴는 등록되지 않은 메뉴입니다.")

        elif meal_time.lower() == "dinner":
            if menu in self.dinner:
                self.dinner.remove(menu)
            else:
                print("해당 메뉴는 등록되지 않은 메뉴입니다.")

        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")

        # save temp_menu.json
        self.save_temp_menu()

    def clear_menu(self):       # lunch, dinner, temp all clear
        self.lunch = []
        self.dinner = []
        self.temp_menu = {}

    def save_temp_menu(self):
        """
            temp_menu saving method
            using in add_menu(), delete_menu() method
        """
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}

        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')
        # only write
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.temp_menu, file, ensure_ascii=False, indent=4)

    def load_temp_menu(self):
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}

        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, f'{self.name}_temp_menu.json')

        if os.path.exists(filename):
            # only read
            with open(filename, 'r', encoding='utf-8') as file:
                self.temp_menu = json.load(file)

    def submit(self):
        """
            temp_menu.json 파일의 "lunch", "dinner" 데이터를
            원본 test.json 파일에 덮어씀, 동시에 self.temp_menu 초기화.
        """
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir, 'test.json')

        # read and write
        with open(filename, 'r+', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                # if test.json is empty, data = []
                data = []

            for restaurant_data in data:
                if restaurant_data["name"] == self.name:
                    restaurant_data["lunch_menu"] = self.temp_menu["lunch"]
                    restaurant_data["dinner_menu"] = self.temp_menu["dinner"]
                    # 파일 내용을 처음으로 되돌림
                    file.seek(0)
                    # 수정된 데이터를 파일에 씀
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    break
            else:
                print("[Error]: Restaurant doesn't exist in test.json file.")

        current_dir = os.path.dirname(__file__)
        temp_menu_path = os.path.join(current_dir, f'{self.name}_temp_menu.json')
        if os.path.exists(temp_menu_path):
            self.lunch, self.dinner = [], []
            self.save_temp_menu()
            # 임시 파일 삭제
            os.remove(temp_menu_path)
            # print("temp_menu.json 파일이 삭제 되었습니다.")
        else:
            print("temp_menu.json 파일이 존재하지 않습니다.")

    def __str__(self):
        return f"Restaurant: {self.name}, Lunch: {self.lunch}, Dinner: {self.dinner}, Location: {self.location}"


if __name__ == "__main__":
    identification = "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6"
    rest = Restaurant.by_id(identification)
