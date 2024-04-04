import os
import json

class Restaurant:   #식당 개체 생성(정보: 아이디, 식당명, 점심리스트, 저녁리스트, 교내외 위치)
    #초기화
    id , name, location = "", "", ""
    lunch, dinner = [], []
    temp_menu, final_menu = {}, {}


    def __init__(self, name, lunch, dinner, location):
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location


    @classmethod
    def by_id(cls, rest_name):
        nametable = ['미가', '세미콘', '수호']
        if rest_name in nametable:
            #test.json : {id:"", name: "", lunch : "" ...}
            current_dir = os.path.dirname(__file__)
            filename = os.path.join(current_dir, 'test.json')

            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for restaurant_data in data:
                    #id 검사
                    if restaurant_data["name"] == rest_name:
                        #초깃값 할당 및 객체 생성
                        return cls(rest_name, restaurant_data["lunch_menu"],
                                   restaurant_data["dinner_menu"], restaurant_data["location"])

        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{rest_name}'")




    def add_menu(self, meal_time, menu):         #단일 메뉴 추가 메서드
        if meal_time.lower() == "lunch":
            self.lunch.append(menu)
        elif meal_time.lower() == "dinner":
            self.dinner.append(menu)
        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")


    def delete_menu(self, meal_time, menu):         #단일 메뉴 삭제 메서드
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




    def get_temp_menus(self)-> dict:                #임시저장 메뉴 불러오기
        self.temp_menu = {"lunch": self.lunch, "dinner": self.dinner}
        return self.temp_menu


    def submit(self)-> dict:                               #확정 메뉴 불러오기 및 temp clear
        self.final_menu = {"lunch": self.lunch, "dinner": self.dinner}
        #초기화
        self.lunch = []
        self.dinner = []
        return self.final_menu





if __name__ == "__main__":
    restaurant = "미가"
    rest = Restaurant.by_id(restaurant)


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
