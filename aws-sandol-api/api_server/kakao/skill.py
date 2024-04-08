
from abc import abstractmethod
from typing import Optional, overload

from .itemcard import Head, ImageTitle, Item, ItemList, ItemListSummary

from .validatiion import validate_str, validate_type
from .common import (
    Action, Button, Buttons, ListItem, ListItems, Profile, Thumbnail,
    Thumbnails)
from .response import ParentSkill


class Carousel(ParentSkill):
    name = "carousel"

    def __init__(
            self,
            items: Optional[list[ParentSkill]] = None,
            solo_mode: bool = True):

        if items is None:
            items = []

        super().__init__(solo_mode)

        self.items = items
        self.type = None
        if not self.is_empty:
            self.type = type(self.items[0])
        self.set_solomode()

    @property
    def is_empty(self):
        return len(self.items) == 0

    def add_item(self, item: ParentSkill):
        if self.is_empty:
            self.type = type(item)
        else:
            assert self.type is not None
            assert isinstance(
                item, self.type), "Carousel 내부의 객체는 동일한 타입이어야 합니다."

        item.solo_mode = False
        self.items.append(item)

    def remove_item(self, item: ParentSkill):
        self.items.remove(item)

    def validate(self):
        super().validate()
        assert len(self.items) > 0, "Carousel은 최소 1개의 객체를 포함해야 합니다."
        assert self.type is not None
        validate_type(
            (TextCard, BasicCard, CommerceCard, ListCard, ItemCard),
            self.type(),
            disallow_none=True,
        )
        validate_type(self.type, *self.items, disallow_none=True)
        for skill in self.items:
            assert (
                not skill.solo_mode
            ), (
                "Carousel 내부의 객체는 solo_mode가 False여야 합니다."
            )
            skill.validate()

    def set_solomode(self, solo_mode: bool = False):
        for skill in self.items:
            skill.solo_mode = solo_mode

    def get_response_content(self):
        assert self.type is not None
        return {
            "type": self.type.name,
            "items": [skill.get_response_content() for skill in self.items]
        }


class SimpleTextResponse(ParentSkill):
    """
    카카오톡 응답 형태 SimpleText의 객체를 생성하는 클래스

    Attributes:
        text (str): 응답할 텍스트

    Raises:
        ValueError: text가 문자열이 아닌 경우
    """
    name = "simpleText"

    def __init__(self, text: str, solo_mode: bool = True):
        super().__init__(solo_mode)
        self.text = text

    def validate(self):
        super().validate()
        return validate_str(self.text)

    def get_response_content(self):
        return {
            "text": self.text
        }


class SimpleImageResponse(ParentSkill):
    """
    카카오톡 응답 형태 SimpleImage의 객체를 생성하는 클래스

    Attributes:
        image_url (str): 이미지의 URL
        alt_text (str): 대체 텍스트

    Raises:
        ValueError: image_url, alt_text가 문자열이 아닌 경우
    """
    name = "simpleImage"

    def __init__(self, image_url: str, alt_text: str):
        super().__init__()
        self.image_url = image_url
        self.alt_text = alt_text

    def validate(self):
        super().validate()
        return validate_str(self.image_url, self.alt_text)

    def get_response_content(self):
        return {
            "imageUrl": self.image_url,
            "altText": self.alt_text
        }


class ParentCard(ParentSkill):
    """
    부모 카드 클래스입니다.

    Attributes:
        buttons (Buttons): 버튼 객체입니다.
    """

    def __init__(self, buttons: Optional[Buttons] = None):
        super().__init__()
        self.buttons = buttons

    def set_buttons(self, buttons: Buttons):
        """
        버튼을 설정합니다.

        Parameters:
            buttons (Buttons): 설정할 버튼 객체
        """
        self.buttons = buttons

    def validate(self):
        super().validate()
        validate_type(Buttons, self.buttons)

    @overload
    def add_button(self, button: Button) -> None: ...

    @overload
    def add_button(
        self,
        label: str,
        action: str | Action,
        webLinkUrl: Optional[str] = None,
        message_text: Optional[str] = None,
        phoneNumber: Optional[str] = None,
        blockId: Optional[str] = None,
        extra: Optional[dict] = None): ...

    def add_button(self, *args, **kwargs) -> None:
        """버튼을 추가합니다.

        Button 객체 또는 Button 생성 인자를 받아 버튼 리스트에 추가합니다.

        Button 객체를 받은 경우
        Args:
            button (Button): 추가할 Button 객체

        Button 생성 인자를 받은 경우
        Args:
            label (str): 버튼의 텍스트
            action (str): 버튼의 동작
            webLinkUrl (str): 웹 링크
            messageText (str): 메시지
            phoneNumber (str): 전화번호
            blockId (str): 블록 ID
            extra (dict): 스킬 서버에 추가로 전달할 데이터

        Raises:
            InvalidTypeError: 받거나 생성한 Button 객체가 Button이 아닌 경우
        """
        if self.buttons is None:
            self.buttons = Buttons()
        self.buttons.add_button(*args, **kwargs)

    def remove_button(self, button):
        """
        버튼을 제거합니다.

        Parameters:
            button: 제거할 버튼 객체
        """
        assert self.buttons is not None
        self.buttons.delete_button(button)

    @abstractmethod
    def get_response_content(self): ...


class TextCard(ParentCard):
    """
    카카오톡 응답 형태 TextCard의 객체를 생성하는 클래스

    Args:
        title (Optional[str], optional): 카드 제목. Defaults to None.
        description (Optional[str], optional): 카드 설명. Defaults to None.
        buttons (Optional[Buttons], optional): 카드 버튼 정보. Defaults to None.
    """
    name = "textCard"

    def __init__(
            self,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[Buttons] = None):
        super().__init__(buttons=buttons)
        self.title = title
        self.description = description

    def validate(self):
        """
        객체가 카카오톡 응답 형태에 맞는지 확인합니다.

        title과 description 중 최소 하나는 None이 아니어야 합니다.
        """
        super().validate()
        if self.title is None and self.description is None:
            raise ValueError(
                "title과 description 중 최소 하나는 None이 아니어야 합니다.")
        if self.title is None:
            validate_str(self.description)
        else:
            validate_str(self.title)

    def get_response_content(self):
        return self.create_dict_with_non_none_values(
            title=self.title,
            description=self.description,
            buttons=self.buttons.render() if self.buttons else None
        )


class BasicCard(ParentCard):
    """
    카카오톡 응답 형태 BasicCard의 객체를 생성하는 클래스

    Args:
        thumbnail (Thumbnail): 썸네일 이미지 정보
        title (Optional[str] optional): 카드 제목. Defaults to None.
        description (Optional[str] optional): 카드 설명. Defaults to None.
        buttons (Optional[Buttons] optional): 카드 버튼 정보. Defaults to None.
        forwardable (bool, optional): 카드 전달 가능 여부. Defaults to False.
    """
    name = "basicCard"

    def __init__(
            self,
            thumbnail: Thumbnail,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[Buttons] = None,
            forwardable: bool = False):
        super().__init__(buttons=buttons)
        self.thumbnail = thumbnail
        self.title = title
        self.description = description
        self.forwardable = forwardable

    def validate(self):
        super().validate()
        validate_str(self.title, self.description)

    def get_response_content(self):
        return self.create_dict_with_non_none_values(
            thumbnail=self.thumbnail.render(),
            title=self.title,
            description=self.description,
            buttons=self.buttons.render() if self.buttons else None,
            forwardable=self.forwardable
        )


class CommerceCard(ParentCard):

    name = "commerceCard"

    def __init__(
        self,
        price: int,
        thumbnails: Thumbnails,
        title: Optional[str] = None,
        description: Optional[str] = None,
        buttons: Optional[Buttons] = None,
        profile: Optional[Profile] = None,
        currency: Optional[str] = None,
        discount: Optional[str] = None,
        discount_rate: Optional[str] = None,
        discount_price: Optional[str] = None,
    ):
        super().__init__(buttons=buttons)
        self.price = price
        self.thumbnails = thumbnails
        self.title = title
        self.description = description
        self.currency = currency
        self.discount = discount
        self.discount_rate = discount_rate
        self.discount_price = discount_price
        self.profile = profile

    def validate(self):
        super().validate()

    def get_response_content(self):
        return self.create_dict_with_non_none_values(
            price=self.price,
            thumbnails=self.thumbnails.render(),
            title=self.title,
            description=self.description,
            currency=self.currency,
            discount=self.discount,
            discountRate=self.discount_rate,
            discountPrice=self.discount_price,
            profile=self.profile.render() if self.profile else None,
            buttons=self.buttons.render() if self.buttons else None,
        )


class ListCard(ParentCard):

    name = "listCard"

    def __init__(
            self,
            header: ListItem | str,
            items: ListItems,
            buttons: Optional[Buttons] = None,):
        super().__init__(buttons=buttons)
        if isinstance(header, str):
            header = ListItem(title=header)
        else:
            self.header = header
        self.items = items

    def validate(self):
        super().validate()
        validate_type(self.header, ListItem)
        validate_type(self.items, ListItems)

    def get_response_content(self):
        return self.create_dict_with_non_none_values(
            header=self.header.render(),
            items=self.items.render(),
            buttons=self.buttons.render() if self.buttons else None,
        )


class ItemCard(ParentCard):

    name = "itemCard"

    def __init__(
            self,
            item_list: ItemList,
            thumbnail: Optional[Thumbnail] = None,
            head: Optional[Head] = None,
            profile: Optional[Profile] = None,
            image_title: Optional[ImageTitle] = None,
            item_list_alignment: Optional[str] = None,
            item_list_summary: Optional[ItemListSummary] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[Buttons] = None,
            buttonLayout: Optional[str] = None):
        super().__init__(buttons=buttons)
        self.item_list = item_list
        self.thumbnail = thumbnail
        self.head = head
        self.profile = profile
        self.image_title = image_title
        self.item_list_alignment = item_list_alignment
        self.item_list_summary = item_list_summary
        self.title = title
        self.description = description
        self.buttonLayout = buttonLayout

    def validate(self):
        super().validate()
        validate_type(self.item_list, ItemList)
        validate_type(self.thumbnail, Thumbnail)
        validate_type(self.head, Head)
        validate_type(self.profile, Profile)
        validate_type(self.image_title, ImageTitle)
        validate_type(self.item_list_summary, ItemListSummary)
        validate_str(self.title, self.description, self.buttonLayout)

    def get_response_content(self):
        assert self.thumbnail is not None
        assert self.head is not None
        assert self.profile is not None
        assert self.image_title is not None
        assert self.item_list is not None
        assert self.item_list_summary is not None
        return self.create_dict_with_non_none_values(
            thumbnail=self.thumbnail.render(),
            head=self.head.render(),
            profile=self.profile.render(),
            imageTitle=self.image_title.render(),
            item_list=self.item_list.render(),
            itemListAlignment=self.item_list_alignment,
            itemListSummary=self.item_list_summary.render(),
            title=self.title,
            description=self.description,
            buttonLayout=self.buttonLayout,
            buttons=self.buttons.render() if self.buttons else None,
        )

    @overload
    def add_item(self, item: Item): ...
    @overload
    def add_item(self, title: str, description: str): ...

    def add_item(self, *args, **kwargs):
        self.item_list.add_item(*args, **kwargs)

    @overload
    def remove_item(self, item: Item): ...
    @overload
    def remove_item(self, index: int): ...

    def remove_item(self, arg):
        self.item_list.remove_item(arg)


if __name__ == "__main__":
    # 사용 예시
    simple_text_response = SimpleTextResponse("이것은 간단한 텍스트 메시지입니다.")
    print(simple_text_response.get_dict())
