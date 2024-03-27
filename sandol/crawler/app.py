import os
import json
import boto3
from bs4 import BeautifulSoup
import requests

filename = r'test.json'

class Restaurant:   #식당 개체 생성(정보: 식당명, 점심리스트, 저녁리스트, 교내외 위치)
    name = ""
    lunch = []
    dinner = []
    location = ""

    def __init__(self, name, lunch, dinner, location):
        self.name = name
        self.lunch = lunch
        self.dinner = dinner
        self.location = location


def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def get_meals(data) -> list:
    restaurants = []
    for item in data:
        name = item.get('name', '')
        lunch = item.get('lunch_menu', [])
        dinner = item.get('dinner_menu', [])
        location = item.get('location', '')
        restaurant = Restaurant(name, lunch, dinner, location)
        restaurants.append(restaurant)
    return restaurants






data = read_json(filename)
restaurants = get_meals(data)
#
# 결과 출력
for restaurant in restaurants:
    lunch = ', '.join(restaurant.lunch)
    dinner = ', '.join(restaurant.dinner)
    print(f"Restaurant: {restaurant.name}, Lunch: {lunch}, Dinner: {dinner}, Location: {restaurant.location}")

