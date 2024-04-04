from typing import Optional, overload

from .common import Common, Link
from .validatiion import validate_str, validate_int, validate_type


class Thumbnail(Common):
    def __init__(self, image_url: str, wdith: Optional[int] = None, height: Optional[int] = None,
                 link: Optional[Link] = None):
        super().__init__()
        self.image_url = image_url
        self.width = wdith
        self.height = height
        self.link = link

    def validate(self):
        validate_str(self.image_url, disallow_none=True)
        validate_int(self.width, self.height)

    def render(self):
        self.validate()
        return self.create_dict_with_non_none_values(
            imageUrl=self.image_url,
            width=self.width,
            height=self.height,
            link=self.link.render()
        )


class Head(Common):
    def __init__(self, title: str):
        super().__init__()
        self.title = title

    def validate(self):
        validate_str(self.title)

    def render(self):
        self.validate()
        return {'title': self.title}


class ImageTitle(Common):
    def __init__(self, title: str, description: Optional[str] = None, image_url: Optional[str] = None):
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url

    def validate(self):
        validate_str(self.title, disallow_none=True)
        validate_str(self.description)

    def render(self):
        self.validate()
        return self.create_dict_with_non_none_values(
            title=self.title,
            description=self.description,
            imageUrl=self.image_url
        )


class Item(Common):
    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description

    def validate(self):
        validate_str(self.title, self.description, disallow_none=True)

    def render(self):
        self.validate()
        return self.create_dict_with_non_none_values(
            title=self.title,
            description=self.description
        )


class ItemList(Common):
    def __init__(self, item_list: Optional[list[Item]] = None):
        super().__init__()
        if item_list is None:
            item_list = []
        self._item_list = item_list

    def validate(self):
        assert len(self._item_list) > 0, "ItemList에는 최소 1개 이상의 Item이 있어야 합니다."
        validate_type(Item, *[self._item_list], disallow_none=True)

    @overload
    def add_item(self, item: Item): ...
    @overload
    def add_item(self, title: str, description: str): ...

    def add_item(self, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], Item):
                self._item_list.append(args[0])
            elif 'description' in kwargs:
                self._item_list.append(Item(*args, **kwargs))
        else:
            self._item_list.append(Item(*args, **kwargs))

    def __add__(self, other):
        if isinstance(other, Item):
            self.add_item(other)
        elif isinstance(other, ItemList):
            self.add_items(other._item_list)
        return self

    def add_items(self, items: list[Item]):
        self._item_list.extend(items)

    @overload
    def remove_item(self, item: Item): ...
    @overload
    def remove_item(self, index: int): ...

    def remove_item(self, arg):
        if isinstance(arg, Item):
            self._item_list.remove(arg)
        elif isinstance(arg, int):
            self._item_list.pop(arg)

    def render(self):
        self.validate()
        assert self._item_list is not None
        return [item.render() for item in self._item_list]


class ItemListSummary(Item):
    ...


class Profile(Common):
    def __init__(self, title: str, image_url: Optional[str] = None, width: Optional[int] = None,
                 height: Optional[int] = None):
        super().__init__()
        self.title = title
        self.image_url = image_url
        self.width = width
        self.height = height

    def validate(self):
        validate_str(self.title, disallow_none=True)
        validate_str(self.image_url)
        validate_int(self.width, self.height)

    def render(self):
        self.validate()
        return self.create_dict_with_non_none_values(
            title=self.title,
            imageUrl=self.image_url,
            width=self.width,
            height=self.height
        )
