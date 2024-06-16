"""카카오톡 챗봇 응답 출력 요소인 컴포넌트를 정의합니다.

카카오톡 챗봇 응답중 SkillTemplate으로 반환할 때
사용되는 컴포넌트를 정의합니다.

컴포넌트는 크게 3가지로 나눌 수 있습니다.
- Simple: 단순한 텍스트, 이미지를 출력하는 컴포넌트
- Card: 텍스트, 이미지, 버튼 등을 포함하는 카드 컴포넌트
- Common: 공통적으로 사용되는 컴포넌트

Modules:
    base: 컴포넌트의 기본이 되는 클래스를 정의합니다.
    card: 카드 컴포넌트를 정의합니다.
    common: 공통적으로 사용되는 컴포넌트를 정의합니다.
    itemcard: ItemCardComponent와 그 하위 컴포넌트를 정의합니다.
    simple: 단순한 컴포넌트를 정의합니다.
"""
from .simple import (
    CarouselComponent, SimpleTextComponent, SimpleImageComponent)
from .card import (
    TextCardComponent, BasicCardComponent, CommerceCardComponent,
    ListCardComponent, ItemCardComponent)
from .common import Link, Thumbnail, Profile, ListItem, Button
from .itemcard import (
    ItemThumbnail, ImageTitle, Item, ItemListSummary,
    ItemProfile
)


__all__ = [
    "CarouselComponent", "SimpleTextComponent", "SimpleImageComponent",
    "TextCardComponent",
    "BasicCardComponent", "CommerceCardComponent",
    "ListCardComponent", "ItemCardComponent",
    "Link", "Thumbnail", "Profile", "ListItem", "Button",
    "ItemThumbnail", "ImageTitle", "Item", "ItemListSummary",
    "ItemProfile"
]
