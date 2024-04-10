from .cafeteria_view import Restaurant, get_meals
from .cafeteria_view import Restaurant as ViewRestaurant


# view 모듈에서 사용자가 직접 호출할 수 있는 함수 정의.
# 각 점포 별 계정 id로 식별
def get_view(identification):
    return ViewRestaurant.by_id(identification)


# registration 모듈에서 사용자가 직접 호출할 수 있는 함수 정의
# 각 점포 별 계정 id로 식별


__all__ = ["Restaurant", "get_meals"]
