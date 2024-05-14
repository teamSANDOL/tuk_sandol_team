from .base import ParentComponent
from .card import (
    TextCardComponent, BasicCard,
    CommerceCardComponent, ItemCardComponent, ListCardComponent)
from ...validation import validate_str, validate_type


class CarouselComponent(ParentComponent):
    """카카오톡 출력 요소 Carousel의 객체를 생성하는 클래스

    가로로 출력 요소(ParentComponent)를 나열할 때 사용합니다.
    Carousel 내부 객체는 동일한 타입이어야 합니다.

    Attributes:
        items (list[ParentComponent]): CarouselComponent에 포함된 객체 리스트
        solo_mode (bool): CarouselComponent 내부 객체의 solo_mode 설정

    example:
        >>> carousel = CarouselComponent()
        >>> carousel.add_item(TextCard(title="제목", description="설명"))
        >>> carousel.add_item(TextCard(title="제목2", description="설명2"))
        >>> carousel.get_dict()
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "items": [
                                {
                                    "title": "제목",
                                    "description": "설명"
                                },
                                {
                                    "title": "제목2",
                                    "description": "설명2"
                                }
                            ]
                        }
                    }
                ]
            }
    """
    name = "carousel"

    def __init__(
            self,
            *items: ParentComponent):
        """Carousel 객체를 생성합니다.

        items를 받아 객체 리스트를 생성합니다.
        만약 items가 비어있지 않으면 첫 번째 객체의 타입을 type에 저장합니다.
        이후 items에 추가되는 객체는 type과 동일한 타입이어야 합니다.

        Args:
            items (tuple[ParentComponent], optional):
                        CarouselComponent에 포함할 객체 리스트. Defaults to None.
        """

        self.items: list[ParentComponent] = [*items]
        self.type = None
        if not self.is_empty:
            self.type = type(self.items[0])

    @property
    def is_empty(self):
        """CarouselComponent이 비어있는지 확인합니다.(super 참고)

        Returns:
            bool: CarouselComponent이 비어있으면 True, 아니면 False
        """
        return not bool(self.items)

    def add_item(self, item: ParentComponent):
        """CarouselComponent에 객체를 추가합니다.

        만약 CarouselComponent이 비어있으면 객체의 타입을 type에 저장합니다.
        아니면 추가되는 객체가 type과 동일한 타입인지 확인합니다.

        Args:
            item (ParentComponent): 추가할 객체, 아래 클래스 중 하나
                        (TextCardComponent, BasicCardComponent,
                        CommerceCardComponent, ListCardComponent,
                        ItemCardComponent)

        Raises:
            AssertionError: CarouselComponent 내부의 객체는 동일한 타입이 아닌 경우
        """
        if self.is_empty:
            self.type = type(item)
        else:
            assert self.type is not None
            assert isinstance(
                item, self.type), "CarouselComponent 내부의 객체는 동일한 타입이어야 합니다."

        self.items.append(item)

    def remove_item(self, item: ParentComponent):
        """CarouselComponent에서 객체를 제거합니다.

        Args:
            item (ParentComponent): 제거할 객체
        """
        self.items.remove(item)

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        Raises:
            AssertionError: CarouselComponent은 최소 1개의 객체를 포함해야 합니다.
            AssertionError: CarouselComponent 내부 객체는 서로 동일한 타입이어야 합니다.
        """
        super().validate()
        assert len(self.items) > 0, "CarouselComponent은 최소 1개의 객체를 포함해야 합니다."
        assert self.type is not None

        if self.type not in (
                TextCardComponent, BasicCard, CommerceCardComponent,
                ListCardComponent, ItemCardComponent):
            raise AssertionError((
                "CarouselComponent 내부 객체는 "
                "TextCardComponent, BasicCardComponent, "
                "CommerceCardComponent, ListCardComponent, ItemCardComponent "
                "중 하나여야 합니다."))

        validate_type(self.type, *self.items, disallow_none=True)
        for component in self.items:
            component.validate()

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        CarouselComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.
        ex) {
                "type": "carousel",
                "items": [
                    item1.get_response_content(), item2.get_response_content(),
                    ]
            }

        Returns:
            dict: 응답 내용
        """
        self.validate()
        assert self.type is not None
        return {
            "type": self.type.name,
            "items": [component.render() for component in self.items]
        }


class SimpleTextComponent(ParentComponent):
    """카카오톡 출력 요소 SimpleText의 객체를 생성하는 클래스

    SimpleTextComponent는 텍스트 만을 출력하는 요소입니다.

    Attributes:
        text (str): 응답할 텍스트

    Raises:
        ValueError: text가 문자열이 아닌 경우

    example:
        >>> simple_text = SimpleTextComponent("안녕하세요")
        >>> simple_text.render()
        {
            "text": "안녕하세요"
        }
    """
    name = "simpleText"

    def __init__(self, text: str):
        """SimpleTextComponent 객체를 생성합니다.

        Args:
            text (str): 응답할 텍스트
        """
        self.text = text

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        Raises:
            ValueError: text가 문자열이 아닌 경우
        """
        super().validate()
        return validate_str(self.text)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        SimpleTextComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.

        Returns:
            dict: 응답 내용
        """
        self.validate()
        return {
            "text": self.text
        }


class SimpleImageComponent(ParentComponent):
    """카카오톡 출력 요소 SimpleImage의 객체를 생성하는 클래스

    SimpleImageComponent는 이미지 만을 출력하는 요소입니다.

    Attributes:
        image_url (str): 이미지의 URL
        alt_text (str): 대체 텍스트

    Raises:
        ValueError: image_url, alt_text가 문자열이 아닌 경우

    example:
        >>> simple_image = SimpleImageComponent(
                image_url="http://example.com/image.jpg",
                alt_text="이미지 설명"
            )
        >>> simple_image.render()
        {
            "imageUrl": "http://example.com/image.jpg",
            "altText": "이미지 설명"
        }
    """
    name = "simpleImage"

    def __init__(self, image_url: str, alt_text: str):
        """SimpleImageComponent 객체를 생성합니다.

        이미지의 URL과 대체 텍스트를 입력받아 객체를 생성합니다.
        이미지는 URL로만 제공되며, 이미지 파일 자체는 전달할 수 없습니다.

        Args:
            image_url (str): 이미지의 URL
            alt_text (str): 대체 텍스트
        """
        super().__init__()
        self.image_url = image_url
        self.alt_text = alt_text

    def validate(self):
        """객체가 카카오톡 출력 요소에 맞는지 확인합니다.(super 참고)

        Raises:
            ValueError: image_url, alt_text가 문자열이 아닌 경우
        """
        super().validate()
        return validate_str(self.image_url, self.alt_text)

    def render(self):
        """객체의 응답 내용을 반환합니다.(super 참고)

        SimpleImageComponent 객체의 응답 내용을 반환합니다.
        이 응답 내용을 이용하여 render() 메서드에서 최종 응답을 생성합니다.

        Returns:
            dict: 응답 내용
        """
        self.validate()
        return {
            "imageUrl": self.image_url,
            "altText": self.alt_text
        }
