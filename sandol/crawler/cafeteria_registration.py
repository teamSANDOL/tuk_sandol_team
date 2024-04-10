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
                        new_class = type(class_name, (Restaurant,), {})  # 클래스 이름을 각 식당명으로 규정
                        # 생성된 클래스로 객체를 생성하여 반환
                        return new_class(restaurant_data["name"], restaurant_data["lunch_menu"],
                                         restaurant_data["dinner_menu"], restaurant_data["location"])

        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{id_address}'")

    def add_menu(self, meal_time, menu):         # 단일 메뉴 추가 메서드
        if not isinstance(meal_time, str):
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

        if meal_time.lower() == "lunch":
            self.lunch.append(menu)
        elif meal_time.lower() == "dinner":
            self.dinner.append(menu)
        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")

        # temp 갱신
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}

    def delete_menu(self, meal_time, menu):         # 단일 메뉴 삭제 메서드
        if not isinstance(meal_time, str):
            raise TypeError("meal_time should be a string 'lunch' or 'dinner'.")

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

        # temp 갱신
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}

    def clear_menu(self):       # lunch, dinner, temp 전체 clear
        self.lunch = []
        self.dinner = []
        self.temp_menu = {}

    def submit(self) -> dict:  # 확정 메뉴 불러오기 및 temp clear
        self.final_menu = self.temp_menu
        self.lunch = []         # 초기화
        self.dinner = []
        self.temp_menu = {}
        return self.final_menu

    def __str__(self):
        return f"Restaurant: {self.name}, Lunch: {self.lunch}, Dinner: {self.dinner}, Location: {self.location}"



if __name__ == "__main__":
    identification = "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6"
    rest = Restaurant.by_id(identification)