import os
import json
from . import settings


class Restaurant:  # 식당 개체 생성(정보: 아이디, 식당명, 점심리스트, 저녁리스트, 교내외 위치)
    def __init__(self, name, lunch, dinner, location):
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location
        self.id = ""
        self.temp = []
        self.menu = []
        self.final_menu = []

    @classmethod
    def by_id(cls, identification):  # 식당 별 access id 조회, 식당 이름으로 객체 생성.
        # settings. RESTAURANT_ACCESS_ID : {id : name}
        restaurant_name = settings.RESTAURANT_ACCESS_ID.get(identification)

        if restaurant_name:
            # test.json : {id:"", name: "", lunch : "" ...}
            current_dir = os.path.dirname(__file__)
            filename = os.path.join(current_dir, 'test.json')

            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for restaurant_data in data:
                    # id 검사
                    if restaurant_data["identification"] == identification:
                        class_name = f"{restaurant_data['name']}"
                        # 클래스 이름을 각 식당명으로 규정
                        new_class = type(class_name, (Restaurant,), {})
                        # 생성된 클래스로 객체를 생성하여 반환
                        return new_class(restaurant_data["name"], restaurant_data["lunch_menu"],
                                         restaurant_data["dinner_menu"], restaurant_data["location"])

        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{identification}'")

    def add_menu(self, meal_time, menu):  # 단일 메뉴 추가 메서드
        if meal_time.lower() == "lunch":
            self.lunch.append(menu)
        elif meal_time.lower() == "dinner":
            self.dinner.append(menu)
        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")

    def delete_menu(self, meal_time, menu):  # 단일 메뉴 삭제 메서드
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

    def get_temp_menus(self) -> dict:  # 임시저장 메뉴 불러오기
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}
        return self.temp_menu

    def submit(self) -> dict:  # 확정 메뉴 불러오기 및 temp clear
        self.final_menu = {"lunch": self.lunch, "dinner": self.dinner}
        # 초기화
        self.lunch = []
        self.dinner = []
        return self.final_menu


def get_meals() -> list:
    current_dir = os.path.dirname(__file__)
    filename = os.path.join(current_dir, 'test.json')

    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 식당 목록 리스트
    restaurants = []

    for item in data:
        name = item.get('name', '')
        lunch = item.get('lunch_menu', [])
        dinner = item.get('dinner_menu', [])
        location = item.get('location', '')

        class_name = f"{item['name']}"
        new_class = type(class_name, (Restaurant,), {})  # 클래스 이름을 각 식당명으로 규정

        restaurant = new_class(name, lunch, dinner, location)
        restaurants.append(restaurant)  # 식당 객체 -> 식당 목록 리스트에 추가

    return restaurants


if __name__ == "__main__":
    identification = "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6"
    rest = Restaurant.by_id(identification)

    # restaurants = get_meals()
    # print(restaurants)
    #
    # restaurants.append(rest)
    # print(restaurants)
    #
    # print(rest.get_temp_menus())
    #
    #
    # rest.add_menu("lunch", "kimchi")
    # print(rest.get_temp_menus())
    #
    # rest.delete_menu("dinner", "비빔밥")
    #
    #
    # print(rest.submit())
    # print(rest.get_temp_menus())
