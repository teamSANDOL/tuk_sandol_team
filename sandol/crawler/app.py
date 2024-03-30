# Menu.py

class Menu:
    def __init__(self):
        self.cafeteria_name = {}
        self.lunch_menu = {}
        self.dinner_menu = {}
        #   self.location = {}   추후 location 추가 필요
        self.date ={}   # 날짜 정보 추가 필요


    def upload_cafeteria(self, restaurant_name, location):
        # 식당 이름과 위치를 저장
        self.cafeteria_name[restaurant_name] = location
        return f"{restaurant_name}이(가) {location}에 등록되었습니다."

    def upload_menu(self, restaurant, lunch_menu, dinner_menu):
        # 식당 이름에 따라 점심 메뉴와 저녁 메뉴를 저장
        if restaurant in self.cafeteria_name:
            self.lunch_menu[restaurant] = lunch_menu.split(',')
            self.dinner_menu[restaurant] = dinner_menu.split(',')
            return f"{restaurant}의 메뉴가 등록되었습니다."
        else:
            return f"{restaurant}은(는) 등록되지 않은 식당입니다."


    def reset_menu(self, restaurant):
        # restaurant가 lunch_menu 또는 dinner_menu에 존재하는지 확인
        if restaurant in self.lunch_menu or self.dinner_menu:
            # 해당 식당의 메뉴가 존재하면 삭제
            if restaurant in self.lunch_menu:
                del self.lunch_menu[restaurant]
            if restaurant in self.dinner_menu:
                del self.dinner_menu[restaurant]
            return f"{restaurant}의 메뉴가 초기화되었습니다."
        else:
            return f"{restaurant}은(는) 등록되지 않은 식당입니다."

    def get_lunch_menu(self, restaurant):
        # 특정 식당의 중식 메뉴 반환
        if restaurant in self.lunch_menu:
            return self.lunch_menu[restaurant]
        else:
            return f"{restaurant}의 중식 메뉴가 등록되지 않았습니다."

    def get_dinner_menu(self, restaurant):
        # 특정 식당의 석식 메뉴 반환
        if restaurant in self.dinner_menu:
            return self.dinner_menu[restaurant]
        else:
            return f"{restaurant}의 석식 메뉴가 등록되지 않았습니다."

# 메뉴 객체 생성
menu = Menu()
