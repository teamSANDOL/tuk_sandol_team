import json

class CafeteriaInfo:
    def __init__(self):
        self.cafeteria_name = ""
        self.lunch_menu = []
        self.dinner_menu = []
        self.location = ""

# JSON 파일 읽어오기
with open('CafeteriaInfo.json', 'r', encoding='UTF-8') as json_file:
    data = json.load(json_file)

#print(data)

# 데이터 출력
cafeteria_info = CafeteriaInfo()
cafeteria_info.cafeteria_name = data[0]['cafeteria_name']
cafeteria_info.lunch_menu = data[0]['lunch_menu']
cafeteria_info.dinner_menu = data[0]['dinner_menu']
cafeteria_info.location = data[0]['location']

print(f"Cafeteria Name: {cafeteria_info.cafeteria_name}")
print(f"Lunch Menu: {cafeteria_info.lunch_menu}")
print(f"Dinner Menu: {cafeteria_info.dinner_menu}")
print(f"Location: {cafeteria_info.location}")
