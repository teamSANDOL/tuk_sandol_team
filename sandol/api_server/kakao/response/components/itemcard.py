"""Component의 ItemCard를 구성하는 클래스들을 담고 있는 모듈입니다.

ItemCard는 구성 요소가 다양하며 각 구성 요소는 ItemCard에서만 사용되기 떄문에
Common 모듈에서 독립적인 모듈로 분리하여 ItemCard를 구성하는 클래스들을 담고 있습니다.

classes:
    ItemThumbnail: ItemCard의 썸네일을 담는 클래스
    ImageTitle: ItemCard의 이미지 타이틀을 담는 클래스
    Item: ItemCard의 아이템을 담는 클래스
    ItemList: ItemCard를 구성하는 Item들을 담는 클래스
    ItemListSummary: ItemCard의 아이템 리스트 요약을 담는 클래스
    ItemProfile: ItemCard의 프로필을 담는 클래스
"""
from typing import Optional

from .common import Common, Link
from ...validation import validate_str, validate_int

__all__ = [
    "ItemThumbnail",
    "ImageTitle",
    "Item",
    "ItemListSummary",
    "ItemProfile"
]


class ItemThumbnail(Common):
    """ItemCard의 썸네일을 담는 클래스입니다.

    썸네일은 ItemCard의 상단 이미지입니다.

    Attributes:
        image_url (str): 썸네일 이미지 URL
        width (int): 썸네일 이미지의 너비 정보
        height (int): 썸네일 이미지의 높이 정보
        link (Link): 썸네일 이미지 클릭 시 이동할 링크
    """

    def __init__(
            self,
            image_url: str,
            width: Optional[int] = None,
            height: Optional[int] = None,
            link: Optional[Link] = None):
        """ItemThumbnail을 생성합니다.

        Args:
            image_url (str): 썸네일 이미지 URL
            width (int, optional): 썸네일 이미지의 너비 정보. Defaults to None.
            height (int, optional): 썸네일 이미지의 높이 정보. Defaults to None.
            link (Link, optional): 썸네일 이미지 클릭 시 이동할 링크. Defaults to None."""
        super().__init__()
        self.image_url = image_url
        self.width = width
        self.height = height
        self.link = link

    def validate(self):
        """ItemThumbnail의 유효성을 검사합니다.

        Raises:
            AssertionError: image_url이 None이거나 str이 아닐 경우 발생합니다.
            AssertionError: width 또는 height가 int가 아닐 경우 발생합니다.
        """
        validate_str(self.image_url, disallow_none=True)
        validate_int(self.width, self.height)

    def render(self):
        """ItemThumbnail을 렌더링합니다.

        ex) {
            "imageUrl": "https://example.com/1.jpg",
            "width": 640,
            "height": 640,
            "link": {
                "web": "https://example.com/1",
                "mobile": "https://example.com/1"
            }
        }

        Returns:
            dict: 렌더링된 ItemThumbnail
        """
        self.validate()
        response = {
            "imageUrl": self.image_url,
            "width": self.width,
            "height": self.height,
            "link": self.link.render() if self.link is not None else None
        }
        return self.remove_none_item(response)


class ImageTitle(Common):
    """ItemCard의 이미지 타이틀을 담는 클래스입니다.

    이미지 타이틀은 ItemCard의 상단 이미지 아래에 위치하는 텍스트입니다.
    왼쪽에 텍스트를 표시하고, 이미지를 오른쪽에 표시할 수 있습니다.
    이미지는 필수가 아닙니다.

    Attributes:
        title (str): 이미지 타이틀의 제목
        description (str): 이미지 타이틀의 설명
        image_url (str): 이미지 타이틀의 이미지 URL
    """

    def __init__(
            self,
            title: str,
            description: Optional[str] = None,
            image_url: Optional[str] = None):
        """ImageTitle을 생성합니다.

        Args:
            title (str): 이미지 타이틀의 제목
            description (str, optional): 이미지 타이틀의 설명. Defaults to None.
            image_url (str, optional): 이미지 타이틀의 이미지 URL. Defaults to None.
        """
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url

    def validate(self):
        """ImageTitle의 유효성을 검사합니다.

        Raises:
            AssertionError: title이 None이거나 str이 아닐 경우 발생합니다.
            AssertionError: description이 str이 아닐 경우 발생합니다.
        """
        validate_str(self.title, disallow_none=True)
        validate_str(self.description)

    def render(self) -> dict:
        """ImageTitle을 렌더링합니다.

        ex) {
            "title": "제목",
            "description": "설명",
            "imageUrl": "https://example.com/1.jpg"
        }

        Returns:
            dict: 렌더링된 ImageTitle
        """
        self.validate()
        response = {
            "title": self.title,
            "description": self.description,
            "imageUrl": self.image_url
        }
        return self.remove_none_item(response)


class Item(Common):
    """ItemCard의 아이템을 담는 클래스입니다.

    ItemCard에는 최소 1개 이상의 Item이 있어야 합니다.
    Item은 제목과 설명을 가지고 있습니다.

    Attributes:
        title (str): 아이템의 제목
        description (str): 아이템의 설명
    """

    def __init__(self, title: str, description: str):
        """Item을 생성합니다.

        Args:
            title (str): 아이템의 제목
            description (str): 아이템의 설명
        """
        super().__init__()
        self.title = title
        self.description = description

    def validate(self):
        """Item의 유효성을 검사합니다.

        Raises:
            AssertionError: title이 None이거나 str이 아닐 경우 발생합니다.
            AssertionError: description이 None이거나 str이 아닐 경우 발생합니다."""
        validate_str(self.title, self.description, disallow_none=True)

    def render(self) -> dict:
        """Item을 렌더링합니다.

        ex) {
            "title": "제목",
            "description": "설명"
        }

        Returns:
            dict: 렌더링된 Item
        """
        self.validate()
        response = {
            "title": self.title,
            "description": self.description
        }
        return self.remove_none_item(response)


class ItemListSummary(Item):
    """ItemCard의 아이템 리스트 요약을 담는 클래스입니다.

    Item과 구조가 같지만, ItemListSummary는 아이템 가격 정보를 의미합니다.
    """


class ItemProfile(Common):
    """ItemCard의 프로필을 담는 클래스입니다.

    ItemCard의 프로필은 ItemCard의 썸네일 바로 밑에 위치하는 프로필 정보입니다.

    Attributes:
        title (str): 프로필의 제목
        image_url (str): 프로필 이미지 URL
        width (int): 프로필 이미지의 너비 정보 / 1:1 비율
        height (int): 프로필 이미지의 높이 정보 / 1:1 비율
    """

    def __init__(
            self,
            title: str,
            image_url: Optional[str] = None,
            width: Optional[int] = None,
            height: Optional[int] = None):
        """ItemProfile을 생성합니다.

        Args:
            title (str): 프로필의 제목
            image_url (str, optional): 프로필 이미지 URL. Defaults to None.
            width (int, optional): 프로필 이미지의 너비 정보. Defaults to None.
            height (int, optional): 프로필 이미지의 높이 정보. Defaults to None.
        """
        super().__init__()
        self.title = title
        self.image_url = image_url
        self.width = width
        self.height = height

    def validate(self):
        """ItemProfile의 유효성을 검사합니다.

        Raises:
            AssertionError: title이 None이거나 str이 아닐 경우 발생합니다.
            AssertionError: image_url이 None이거나 str이 아닐 경우 발생합니다.
            AssertionError: width 또는 height가 int가 아닐 경우 발생합니다.
        """
        validate_str(self.title, disallow_none=True)
        validate_str(self.image_url)
        validate_int(self.width, self.height)

    def render(self) -> dict:
        """ItemProfile을 렌더링합니다.

        e.g.: {
            "title": "제목",
            "imageUrl": "https://example.com/1.jpg",
            "width": 640,
            "height": 640
        }

        Returns:
            dict: 렌더링된 ItemProfile
        """
        self.validate()
        response = {
            "title": self.title,
            "imageUrl": self.image_url,
            "width": self.width,
            "height": self.height
        }
        return self.remove_none_item(response)
