import json
import settings


class Restaurant:
    id, name, location = "", "", ""
    temp_lunch, temp_dinner = [], []
    temp_menu, final_menu = {}, {}

    def __init__(self, id, name, lunch, dinner, location):
        self.id = id
        self.name = name
        self.location = location
        self.temp_lunch = lunch
        self.temp_dinner = dinner


    @classmethod
    def by_id(cls, id):
        cls.name = settings.RESTAURANT_ACCESS_ID.get(id)
        if cls.name:
            return cls
        else:
            raise ValueError(f"해당 식당을 찾을 수 없습니다. ID: '{id}'")


    def add_menu(cls, meal_time, menu):
        if meal_time.lower() == "lunch":
            cls.temp_lunch.append(menu)
        elif meal_time.lower() == "dinner":
            cls.temp_dinner.append(menu)
        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")



    def delete_menu(cls, meal_time, menu):
        if meal_time.lower() == "lunch":
            if menu in cls.temp_lunch:
                cls.temp_lunch.remove(menu)
                print(f"메뉴 '{menu}'가 점심 리스트에서 삭제되었습니다.")
            else:
                print("해당 메뉴는 등록되지 않은 메뉴입니다.")

        elif meal_time.lower() == "dinner":
            if menu in cls.temp_dinner:
                cls.temp_dinner.remove(menu)
                print(f"메뉴 '{menu}'가 저녁 리스트에서 삭제되었습니다.")
            else:
                print("해당 메뉴는 등록되지 않은 메뉴입니다.")

        else:
            print("[ValueError]: First value should be 'lunch' or 'dinner'.")




    def get_temp_menus(cls):
        return {"lunch": cls.temp_lunch, "dinner": cls.temp_dinner}



    def submit(cls):
        final_menu = {"lunch": cls.temp_lunch, "dinner": cls.temp_dinner}
        return final_menu




def get_meals() -> list:
    filename = r'test.json'
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    restaurants = []

    for item in data:
        id = item.get('id', '')
        name = item.get('name', '')
        lunch = item.get('lunch_menu', [])
        dinner = item.get('dinner_menu', [])
        location = item.get('location', '')
        restaurant = Restaurant(id, name, lunch, dinner, location)
        restaurants.append(restaurant)

    return restaurants





if __name__ == "__main__":
    restaurants = get_meals()

    id = "32d8a05a91242ffb4c64b5630ec55953121dffd83a121d985e26e06e2c457197e6"
    rest = Restaurant.by_id(id)
    rest.add_menu(rest, "lunch", "kimchi")
    rest.add_menu(rest, "Dinner", "rice")

    temp = rest.get_temp_menus(rest)
    submit = rest.submit(rest)

    print(f"Restaurant: {rest.name}, Lunch: {submit['lunch']}, Dinner: {submit['dinner']}, Location: {rest.location}")

    rest.delete_menu(rest, "lunch", "kimchi")
    print(f"Restaurant: {rest.name}, Lunch: {submit['lunch']}, Dinner: {submit['dinner']}, Location: {rest.location}")
