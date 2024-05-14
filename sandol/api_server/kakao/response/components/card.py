from typing import Optional, overload


from .base import ParentCardComponent
from .common import Button, Link, ListItem, Profile, Thumbnail
from ..interactiron import ActionEnum
from .itemcard import (
    ImageTitle, Item, ItemListSummary, ItemProfile, ItemThumbnail)
from ...validation import validate_int, validate_str, validate_type


class TextCardComponent(ParentCardComponent):
    """카카오톡 출력 요소 TextCard의 객체를 생성하는 클래스

    TextCardComponent는 제목과 설명을 출력하는 요소입니다.
    title과 description 중 최소 하나는 None이 아니어야 합니다.

    Args:
        title (Optional[str], optional): 카드 제목. Defaults to None.
        description (Optional[str], optional): 카드 설명. Defaults to None.
        buttons (Optional[list[Button]], optional): 버튼 리스트. Defaults to None.

    example:
        >>> text_card = TextCardComponent(title="제목", description="설명")
        >>> text_card.add_button(
                label="버튼 1", action="message", message_text="버튼 1 클릭"
            )
        >>> text_card.render()
        {
            "title": "제목",
            "description": "설명",
            "buttons": [
                {
                    "label": "버튼 1",
                    "action": "message",
                    "messageText": "버튼 1 클릭"
                }
            ]
        }
    """
    name = "textCard"

    def __init__(
            self,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[list[Button]] = None):
        """TextCardComponent 객체를 생성합니다.

        Args:
            title (Optional[str], optional): 카드의 제목. Defaults to None.
            description (Optional[str], optional): 카드 상세 설명. Defaults to None.
            buttons (Optional[Buttons], optional): 카드의 버튼들. Defaults to None.
        """
        super().__init__(buttons=buttons)
        self.title = title
        self.description = description

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        title과 description 중 최소 하나는 None이 아니어야 합니다.

        raise:
            ValueError: title과 description 중 최소 하나는 None이 아니어야 합니다.
        """
        super().validate()
        if self.title is None and self.description is None:
            raise ValueError(
                "title과 description 중 최소 하나는 None이 아니어야 합니다.")
        if self.title is None:
            validate_str(self.description)
        else:
            validate_str(self.title)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        TextCardComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.
        ex) {
                "title": "제목", # 제목이 없을 경우 미표시
                "description": "설명", # 설명이 없을 경우 미표시
                "buttons": buttons.get_response_content()
            }
        Returns:
            dict: 응답 내용
        """
        self.validate()
        response = {
            "title": self.title,
            "description": self.description,
            "buttons": ([button.render() for button in self.buttons]
                        if self.buttons else None)
        }
        return self.remove_none_item(response)


class BasicCard(ParentCardComponent):
    """카카오톡 출력 요소 BasicCard의 객체를 생성하는 클래스

    BasicCardComponent는 소셜, 썸네일, 프로필 등을 통해서 사진이나 글, 인물 정보 등을 공유할 수 있습니다.
    제목과 설명 외에 썸네일 그룹, 프로필, 버튼 그룹, 소셜 정보를 추가로 포함합니다.
    Thumbnail 객체는 반드시 포함되어야 합니다. 제목과 설명만 있는 TextCardComponent와의 차이점입니다.

    Args:
        thumbnail (Thumbnail): 카드의 상단 이미지
        title (Optional[str] optional): 카드 제목. Defaults to None.
        description (Optional[str] optional): 카드 상세 설명. Defaults to None.
        buttons (Optional[list[Button]], optional): 버튼 리스트. Defaults to None.

    example:
        >>> basic_card = BasicCardComponent(
                thumbnail=Thumbnail(
                    image_url="http://example.com/image.jpg",
                    link=Link(web="http://example.com")
                ),
                title="제목",
                description="설명"
            )
        >>> basic_card.add_button(
                label="버튼 1", action="message", message_text="버튼 1 클릭"
            )
        >>> basic_card.render()
        {
            "thumbnail": {
                "imageUrl": "http://example.com/image.jpg",
                "link": {
                    "web": "http://example.com"
                }
            },
            "title": "제목",
            "description": "설명",
            "buttons": [
                {
                    "label": "버튼 1",
                    "action": "message",
                    "messageText": "버튼 1 클릭"
                }
            ]
        }
    """
    name = "basicCard"

    def __init__(
            self,
            thumbnail: Thumbnail,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[list[Button]] = None,
            forwardable: bool = False):
        """BasicCardComponent 객체를 생성합니다.

        Args:
            thumbnail (Thumbnail): 카드의 상단 이미지
            title (str, optional): 카드 제목. Defaults to None.
            description (str optional): 카드 상세 설명. Defaults to None.
            buttons (list[Button], optional): 버튼 리스트. Defaults to None.
            forwardable (bool, optional): 공유하기 버튼 표시 여부. Defaults to False.
        """
        super().__init__(buttons=buttons)
        self.thumbnail = thumbnail
        self.title = title
        self.description = description
        self.forwardable = forwardable

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        Thumbnail 객체는 반드시 포함되어야 합니다.
        제목과 설명은 문자열이어야 합니다.

        raise:
            InvalidTypeError: Thumbnail 객체가 Thumbnail이 아닌 경우
            ValueError: title과 description이 문자열이 아니어야 합니다.
        """
        super().validate()
        validate_type(Thumbnail, self.thumbnail)
        validate_str(self.title, self.description)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        BasicCard 객체의 응답 내용을 반환합니다.
        ex) {
                "thumbnail": thumbnail.get_response_content(),
                "title": "제목",
                "description": "설명",
                "buttons": buttons.get_response_content(),
                "forwardable": True
            }

        Returns:
            dict: 응답 내용
        """
        self.validate()
        response = {
            "thumbnail": self.thumbnail.render(),
            "title": self.title,
            "description": self.description,
            "buttons": ([button.render() for button in self.buttons]
                        if self.buttons else None),
            "forwardable": self.forwardable
        }
        return self.remove_none_item(response)


class CommerceCardComponent(ParentCardComponent):
    """카카오톡 출력 요소 CommerceCard의 객체를 생성하는 클래스

    CommerceCardComponent는 제품에 대한 소개, 구매 안내 등을 사용자에게 전달할 수 있습니다.
    커머스 카드는 제목과 설명 외에 썸네일 그룹, 프로필, 버튼 그룹, 가격 정보를 추가로 포함합니다.

    discountedPrice 가 존재하면 price, discount, discountRate 과 관계 없이
    무조건 해당 값이 사용자에게 노출됩니다.
    discountRate은 discountedPrice를 필요로 합니다.
    discountedPrice가 주어지지 않으면 사용자에게 >discountRate을 노출하지 않습니다.
    discountRate과 discount가 동시에 있는 경우, discountRate을 우선적으로 노출합니다.

    Attributes:
        price (int): 제품 가격
        thumbnails (list[Thumbnail]): 제품에 대한 사진(현재는 1개만 지원)
        title (Optional[str], optional): 제품의 이름. Defaults to None.
        description (Optional[str], optional): 제품에 대한 상세 설명. Defaults to None.
        buttons (Optional[list[Button]], optional): 버튼 리스트. Defaults to None.
        profile (Optional[Profile], optional): 제품을 판매하는 프로필. Defaults to None.
        currency (Optional[str], optional): 제품을 가격의 통화(현재는 won만 가능).
                                            Defaults to None.
        discount (Optional[str], optional): 제품의 가격에 대한 할인할 금액.
                                            Defaults to None.
        discount_rate (Optional[str], optional): 제품의 가격에 대한 할인율.
                                                    Defaults to None.
        discount_price (Optional[str], optional): 제품의 가격에 대한 할인가(할인된 가격).
                                                    discountRate을 쓰는 경우 필수.
                                                    Defaults to None.

    example:
        >>> commerce_card = CommerceCardComponent(
                price=10999,
                thumbnails=[
                    Thumbnail(image_url="http://example.com/image1.jpg"),
                ],
                title="커머스 카드",
                description="커머스 카드 설명",
                buttons=Buttons(
                    buttons=[
                        Button(
                            label="구매하기", action="webLink",
                            web_link_url="http://example.com")
                    ]
                ),
                profile=Profile(
                    nickname="제품 이름",
                    image_url="http://example.com/image.jpg"
                ),
                currency="won",
                discount=1000,
                discount_rate=10,
                discount_price=9000
            )
        >>> commerce_card.render()
        {
            "price": 10999,
            "thumbnails": {
                "thumbnails": [
                    {
                        "imageUrl": "http://example.com/image1.jpg"
                    }
                ]
            },
            "title": "커머스 카드",
            "description": "커머스 카드 설명",
            "currency": "won",
            "discount": "1000",
            "discountRate": "10",
            "discountPrice": "9000",
            "profile": {
                "nickname": "제품 이름",
                "imageUrl": "http://example.com/image.jpg"
            },
            "buttons": {
                "buttons": [
                    {
                        "label": "구매하기",
                        "action": "webLink",
                        "webLinkUrl": "http://example.com"
                    }
                ]
            }
        }
    """
    name = "commerceCard"

    def __init__(
        self,
        price: int,
        thumbnails: list[Thumbnail] | Thumbnail,
        title: Optional[str] = None,
        description: Optional[str] = None,
        buttons: Optional[list[Button]] = None,
        profile: Optional[Profile] = None,
        currency: Optional[str] = None,
        discount: Optional[int] = None,
        discount_rate: Optional[int] = None,
        discount_price: Optional[int] = None,
    ):
        """CommerceCardComponent 객체를 생성합니다.

        Args: class Docstring 참고
        """
        super().__init__(buttons=buttons)
        self.price = price
        if isinstance(thumbnails, Thumbnail):
            thumbnails = [thumbnails]
        self.thumbnails = thumbnails
        self.title = title
        self.description = description
        self.currency = currency
        self.discount = discount
        self.discount_rate = discount_rate
        self.discount_price = discount_price
        self.profile = profile

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        raise:
            ValueError: price가 int가 아닌 경우
            ValueError: title, description이 문자열이 아닌 경우
            AssertionError: currency가 "won"이 아닌 경우
            ValueError: discount, discount_price, discount_rate가 int가 아닌 경우
            InvalidTypeError: thumbnails의 각 요소가 Thumbnail이 아닌 경우
            InvalidTypeError: profile이 Profile이 아닌 경우
        """
        super().validate()
        validate_int(self.price, disallow_none=True)
        for thumbnail in self.thumbnails:
            validate_type(Thumbnail, thumbnail)
        validate_str(self.title, self.description)
        if self.currency:
            assert self.currency == "won"
        validate_int(
            self.discount, self.discount_price,
            self.discount_rate, self.discount_price)
        validate_type(Profile, self.profile)

    def render(self) -> dict:
        """객체의 응답 내용을 반환합니다.(super 참고)

        CommerceCardComponent 객체의 응답 내용을 반환합니다.
        None인 속성은 미표시됩니다.
        ex) {
                "price": 10000,
                "thumbnails": [thumbnail.render() ...],
                "title": "제목",
                "description": "설명",
                "currency": "won",
                "discount": "1000",
                "discountRate": "10",
                "discountPrice": "9000",
                "profile": profile.render(),
                "buttons": buttons.render()
            }
        Returns:
            dict: 응답 내용
        """
        self.validate()
        response = {
            "price": self.price,
            "thumbnails": [
                thumbnail.render() for thumbnail in self.thumbnails],
            "title": self.title,
            "description": self.description,
            "currency": self.currency,
            "discount": self.discount,
            "discountRate": self.discount_rate,
            "discountPrice": self.discount_price,
            "profile": self.profile.render() if self.profile else None,
            "buttons": ([button.render() for button in self.buttons]
                        if self.buttons else None)
        }
        return self.remove_none_item(response)


class ListCardComponent(ParentCardComponent):
    """카카오톡 출력 요소 ListCard의 객체를 생성하는 클래스

    ListCardComponent는 헤더와 아이템을 포함하며, 헤더는 리스트 카드의 상단에 위치합니다.
    리스트 상의 아이템은 각각의 구체적인 형태를 보여주며, 제목과 썸네일, 상세 설명을 포함합니다.
    header는 ListItem 객체이어야 하지만, str으로 입력받을 경우 ListItem으로 변환됩니다.

    Attributes:
        header (ListItem): 리스트 카드의 헤더
        items (ListItems): 리스트 카드의 아이템들
        max_buttons (int): 버튼 최대 개수. Defaults to 2.
        max_items (int): 아이템 최대 개수. Defaults to 5.
                ListCardComponent가 Carousel로 나타나는 경우 최대 4개로 제한되어 있기 때문에,
                값을 4로 수정해야 합니다.

    example:
        >>> list_card = ListCardComponent(
            header="리스트 카드"
        )
        >>> list_card.add_item(
                ListItem(
                    title="아이템 1",
                    description="아이템 1 설명",
                    image_url="http://example.com/image1.jpg"
                )
            )
        >>> list_card.render()
        {
            "header": {
                "title": "리스트 카드"
            },
            "items": [
                {
                    "title": "아이템 1",
                    "description": "아이템 1 설명",
                    "imageUrl": "http://example.com/image1.jpg"
                }
            ]
        }
    """
    name = "listCard"

    def __init__(
            self,
            header: ListItem | str,
            items: Optional[list[ListItem]] = None,
            buttons: Optional[list[Button]] = None,
            max_buttons: int = 2,
            max_items: int = 5
    ):
        """ListCard 객체를 생성합니다.

        Args:
            header (ListItem | str): 리스트 카드의 상단 항목 str인 경우 ListItem으로 변환됩니다.
            items (ListItems): 리스트 카드의 각각 아이템
            buttons (Optional[Buttons], optional): 리스트 카드의 버튼들.
                                                    Defaults to None.
            max_buttons (int, optional): 버튼 최대 개수. Defaults to 2.
            max_items (int, optional): 아이템 최대 개수. Defaults to 5.
        """
        super().__init__(buttons=buttons)
        if isinstance(header, str):
            self.header = ListItem(title=header)
        else:
            self.header = header
        if items is None:
            items = []
        self.items = items
        self.max_buttons = max_buttons
        self.max_items = max_items

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        raise:
            InvalidTypeError: header가 ListItem이 아닌 경우
            AssertionError: items가 비어있는 경우
            InvalidTypeError: items가 ListItems가 아닌 경우
        """
        super().validate()
        if len(self.items) < 1:
            raise AssertionError("ListCardComponent는 최소 1개의 아이템을 포함해야 합니다.")
        if len(self.items) > self.max_items:
            raise AssertionError(
                f"ListCard는 최대 {self.max_items}개의 아이템을 포함할 수 있습니다.")
        if len(self.buttons) > self.max_buttons:
            raise AssertionError(
                f"ListCard는 최대 {self.max_buttons}개의 버튼을 포함할 수 있습니다.")
        validate_type(ListItem, self.header, disallow_none=True)
        validate_type(ListItem, *self.items)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        ListCardComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.
        ex) {
                "header": header.get_response_content(),
                "items": items.get_response_content(),
                "buttons": buttons.get_response_content()
            }

        Returns:
            dict: 응답 내용
        """
        self.validate()
        response = {
            "header": self.header.render(),
            "items": (
                [item.render() for item in self.items]
                if self.items else None
            ),
            "buttons": (
                [button.render() for button in self.buttons]
                if self.buttons else None
            )
        }
        return self.remove_none_item(response)

    @overload
    def add_item(
            self,
            title: str,
            description: Optional[str] = None,
            image_url: Optional[str] = None,
            link: Optional[Link] = None,  # TODO: 순환참조 주의
            action: Optional[str | ActionEnum] = None,
            block_id: Optional[str] = None,
            message_text: Optional[str] = None,
            extra: Optional[dict] = None) -> "ListCardComponent":
        """ListCardComponent에 아이템을 ListItem 생성 인자로 추가합니다.

        Args:
            title (str): item의 제목
            description (str, optional): item의 설명
            image_url (str, optional): item의 우측 안내 사진
            link (Link, optional): item 클릭 시 동작할 링크
            action (str | Action, optional):
                            itaem 클릭 시 수행될 작업(block 또는 message)
            block_id (str, optional): action이 block인 경우 block_id를 갖는 블록을 호출
            message_text (str, optional):
                            action이 message인 경우 리스트 아이템 클릭 시 전달할 메시지
            extra (dict, optional): 블록 호출시, 스킬 서버에 추가적으로 제공하는 정보

        Returns:
            ListCardComponent: ListItem이 추가된 객체
        """
    @overload
    def add_item(self, item: ListItem) -> "ListCardComponent":
        """ListCardComponent에 아이템을 ListItem 객체로 추가합니다.

        Args:
            item (ListItem): 추가할 ListItem 객체

        Returns:
            ListCardComponent: ListItem이 추가된 객체
        """

    def add_item(self, *args, **kwargs) -> "ListCardComponent":
        """ListCardComponent에 아이템을 추가합니다.

        ListItem 객체 또는 ListItem 생성 인자를 받아 아이템 리스트에 추가합니다.

        Args:
            *args: ListItem 생성 인자 또는 ListItem 객체
            **kwargs: ListItem 생성 인자 또는 ListItem 객체

        Returns:
            ListCardComponent: ListItem이 추가된 객체
        """
        if len(args) == 1 and isinstance(args[0], ListItem):
            self.items.append(args[0])
        elif len(args) == 0 and "item" in kwargs:
            self.items.append(kwargs["item"])
        else:
            item = ListItem(*args, **kwargs)
            self.items.append(item)
        return self

    def remove_item(self, item: ListItem) -> "ListCardComponent":
        """ListCardComponent에서 아이템을 제거합니다.

        Args:
            item (ListItem): 제거할 ListItem 객체
        """
        assert isinstance(item, ListItem)
        if item not in self.items:
            raise ValueError("해당 아이템이 존재하지 않습니다.")
        self.items.remove(item)

        return self


class ItemCardComponent(ParentCardComponent):
    """카카오톡 출력 요소 ItemCard의 객체를 생성하는 클래스

    ItemCardComponent는 메시지 목적에 따른 유관 정보들을 (가격 정보 포함)
    사용자에게 일목요연한 리스트 형태로 전달할 수 있습니다.
    ItemCardComponent는 아이템리스트, 제목, 설명 외에
    썸네일, 프로필, 헤드, 이미지타이틀, 버튼 그룹을 추가로 포함합니다.

    Attributes:
        item_list (list[Item]): Item 객체들이 포함된 리스트
        thumbnail (ItemThumbnail): 상단 이미지
                                단일형: 이미지 비율 2:1 (800*400), 1:1 (800*800)사용 가능
                                케로셀형: 이미지 비율 2:1 (800*400)만 사용 가능
        head (str): 헤드 정보입니다. 프로필과 함께 사용할 수 없습니다.
        profile (ItemProfile): 프로필 정보. 헤드와 함께 사용할 수 없습니다.
        image_title (ImageTitle): 이미지를 동반하는 제목 및 설명 정보입니다.
                                    이미지 우측 정렬 고정 (위치 변경 불가)
        item_list_alignment (str): itemList 및 itemListAlignment 정렬 정보입니다.
                                    (left, right 중 선택)
        item_list_summary (ItemListSummary): 아이템 가격 정보입니다.
                                            사용시 item_list_alignment는 right 권장.
        title (str): 타이틀 정보. description을 넣는 경우, title이 필수입니다.
        description (str): 설명. 사용시 title이 필수입니다.
        button_layout (str): 버튼 정렬 정보. 단일형에서만 사용 가능.
                                (vertical, horizontal 중 선택)
                                미입력시 자동 선택
        buttons (Optional[list[Button]], optional): 버튼 리스트. Defaults to None.
                            단일형: 최대 3개까지 사용 가능
                            케로셀형: 최대 2개까지 사용 가능
    """
    name = "itemCard"

    def __init__(
            self,
            item_list: list[Item],
            thumbnail: Optional[ItemThumbnail] = None,
            head: Optional[str] = None,
            profile: Optional[ItemProfile] = None,
            image_title: Optional[ImageTitle] = None,
            item_list_alignment: Optional[str] = None,
            item_list_summary: Optional[ItemListSummary] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            buttons: Optional[list[Button]] = None,
            button_layout: Optional[str] = None):
        """ItemCardComponent 객체를 생성합니다.

        Args: class Docstring 참고
        """
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
        self.button_layout = button_layout

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 및 하위 클래스 참고)

        raise:
            InvalidTypeError: item_list의 각 요소가 Item이 아닌 경우
            InvalidTypeError: thumbnail가 ItemThumbnail 아닌 경우
            InvalidTypeError: head가 Head가 아닌 경우
            InvalidTypeError: profile가 ItemProfile이 아닌 경우
            InvalidTypeError: image_title가 ImageTitle이 아닌 경우
            InvalidTypeError: item_list_summary가 ItemListSummary이 아닌 경우
            ValueError: title, description, button_layout이 문자열이 아닌 경우
        """
        super().validate()
        for item in self.item_list:
            validate_type(Item, item)
        validate_type(ItemThumbnail, self.thumbnail)
        validate_type(ItemProfile, self.profile)
        validate_type(ImageTitle, self.image_title)
        validate_type(ItemListSummary, self.item_list_summary)
        validate_str(
            self.head, self.title,
            self.description, self.button_layout)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 및 하위 클래스 참고)

        ItemCardComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.
        None인 속성은 미표시됩니다.
        ex) {
                "thumbnail": thumbnail.get_response_content(),
                "head": {"title": "헤드"},
                "profile": profile.get_response_content(),
                "imageTitle": image_title.get_response_content(),
                "itemList": [item.render() ...]
                "itemListAlignment": "left",
                "itemListSummary": item_list_summary.get_response_content(),
                "title": "타이틀",
                "description": "설명",
                "buttonLayout": "vertical",
                "buttons": buttons.get_response_content()
            }

        Returns:
            dict: 응답 내용
        """
        self.validate()
        assert self.item_list is not None

        response = {
            "thumbnail": self.thumbnail.render() if self.thumbnail else None,
            "head": {"title": self.head} if self.head else None,
            "profile": self.profile.render() if self.profile else None,
            "imageTitle": (
                self.image_title.render()
                if self.image_title else None),
            "itemList": [item.render() for item in self.item_list],
            "itemListAlignment": self.item_list_alignment,
            "itemListSummary": (
                self.item_list_summary.render()
                if self.item_list_summary else None),
            "title": self.title,
            "description": self.description,
            "buttonLayout": self.button_layout,
            "buttons": (
                [button.render() for button in self.buttons]
                if self.buttons else None)
        }
        return self.remove_none_item(response)

    @overload
    def add_item(self, item: Item):
        """아이템을 객체로 추가합니다.

        Args:
            item (Item): 추가할 Item 객체
        """
    @overload
    def add_item(self, title: str, description: str):
        """아이템 생성 인자로 아이템을 추가합니다.

        아이템 생성 인자를 받아 Item 객체를 생성하여 아이템 리스트에 추가합니다.

        Args:
            title (str): 아이템의 제목
            description (str): 아이템의 설명
        """

    def add_item(self, *args, **kwargs):
        """아이템을 추가합니다.

        Item 객체 또는 Item 생성 인자를 받아 아이템 리스트에 추가합니다.

        Args:
            *args: Item 생성 인자 또는 Item 객체
            **kwargs: Item 생성 인자 또는 Item 객체
        """
        if len(args) == 1:
            if isinstance(args[0], Item):
                self.item_list.append(args[0])
            elif 'description' in kwargs:
                self.item_list.append(Item(*args, **kwargs))
        else:
            if 'item' in kwargs:
                self.item_list.append(kwargs['item'])
            self.item_list.append(Item(*args, **kwargs))

    @overload
    def remove_item(self, item: Item):
        """아이템을 객체로 제거합니다.

        Args:
            item (Item): 제거할 Item 객체
        """
    @overload
    def remove_item(self, index: int):
        """인덱스로 아이템을 제거합니다.

        Args:
            index (int): 제거할 아이템의 인덱스
        """

    def remove_item(self, *arg, **kwarg):
        """아이템을 제거합니다.

        Item 객체 또는 인덱스를 받아 아이템 리스트에서 제거합니다.

        Args:
            arg: Item 객체 또는 제거할 아이템의 인덱스
        """
        if isinstance(arg[0], Item):
            self.item_list.remove(arg[0])
        elif isinstance(arg[0], int):
            self.item_list.pop(arg[0])
        elif 'item' in kwarg:
            self.item_list.remove(kwarg['item'])
        elif 'index' in kwarg:
            self.item_list.pop(kwarg['index'])
