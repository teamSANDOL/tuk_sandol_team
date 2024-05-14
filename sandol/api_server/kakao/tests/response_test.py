import unittest
from kakao.response import KakaoResponse
from kakao.response.components import (
    BasicCardComponent, CommerceCardComponent, ListCardComponent,
    TextCardComponent, SimpleImageComponent, SimpleTextComponent,
    Button, Link, ListItem, Profile, Thumbnail, CarouselComponent
)


class TestKakaoModule(unittest.TestCase):

    def test_data(self):
        response = KakaoResponse(
            data={
                "msg": "HI",
                "name": "Ryan",
                "position": "Senior Managing Director"
            }
        )

        example = {
            "version": "2.0",
            "data": {
                "msg": "HI",
                "name": "Ryan",
                "position": "Senior Managing Director"
            }
        }
        self.assertDictEqual(example, response.get_dict())

    def test_context(self):
        response = KakaoResponse()
        response.add_context(
            name="abc",
            lifespan=10,
            ttl=60,
            params={
                "key1": "val1",
                "key2": "val2"
            }
        )
        response.add_context(
            name="def",
            lifespan=5,
            params={
                "key3": "1",
                "key4": "true",
                "key5":  "{\"jsonKey\": \"jsonVal\"}"
            }
        )
        response.add_context(
            name="ghi",
            lifespan=0
        )
        example = {
            "version": "2.0",
            "context": {
                "values": [
                    {
                        "name": "abc",
                        "lifeSpan": 10,
                        "ttl": 60,
                        "params": {
                            "key1": "val1",
                            "key2": "val2"
                        }
                    },
                    {
                        "name": "def",
                        "lifeSpan": 5,
                        "params": {
                            "key3": "1",
                            "key4": "true",
                            "key5": "{\"jsonKey\": \"jsonVal\"}"
                        }
                    },
                    {
                        "name": "ghi",
                        "lifeSpan": 0
                    }
                ]
            }
        }
        print(response.get_dict())
        self.assertDictEqual(example, response.get_dict())

    def test_simple_text(self):
        response = KakaoResponse()
        response.add_component(SimpleTextComponent("간단한 텍스트 요소입니다."))
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "간단한 텍스트 요소입니다."
                        }
                    }
                ]
            }
        }
        self.assertDictEqual(example, response.get_dict())

    def test_simple_image(self):
        response = KakaoResponse()
        response.add_component(SimpleImageComponent(
            image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg",
            alt_text="보물상자입니다"
        ))
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleImage": {
                            "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg",
                            "altText": "보물상자입니다"
                        }
                    }
                ]
            }
        }
        self.assertDictEqual(example, response.get_dict())

    def test_text_card(self):
        response = KakaoResponse()
        textcard = TextCardComponent(
            title="챗봇 관리자센터에 오신 것을 환영합니다.",
            description="챗봇 관리자센터로 챗봇을 제작해 보세요. \n카카오톡 채널과 연결하여, 이용자에게 챗봇 서비스를 제공할 수 있습니다.",

        )
        textcard.add_button(
            action="webLink",
            label="소개 보러가기",
            web_link_url="https://chatbot.kakao.com/docs/getting-started-overview/"
        )
        textcard.add_button(
            action="webLink",
            label="챗봇 만들러 가기",
            web_link_url="https://chatbot.kakao.com/"
        )
        response.add_component(textcard)
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "textCard": {
                            "title": "챗봇 관리자센터에 오신 것을 환영합니다.",
                            "description": "챗봇 관리자센터로 챗봇을 제작해 보세요. \n카카오톡 채널과 연결하여, 이용자에게 챗봇 서비스를 제공할 수 있습니다.",
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "소개 보러가기",
                                    "webLinkUrl": "https://chatbot.kakao.com/docs/getting-started-overview/"
                                },
                                {
                                    "action": "webLink",
                                    "label": "챗봇 만들러 가기",
                                    "webLinkUrl": "https://chatbot.kakao.com/"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertDictEqual(example, response.get_dict())

    def test_basic_card(self):
        response = KakaoResponse()
        basiccard = BasicCardComponent(
            title="보물상자",
            description="보물상자 안에는 뭐가 있을까",
            thumbnail=Thumbnail(
                image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
            ),
            buttons=[
                Button(
                    action="message",
                    label="열어보기",
                    message_text="짜잔! 우리가 찾던 보물입니다"
                ),
                Button(
                    action="webLink",
                    label="구경하기",
                    web_link_url="https://e.kakao.com/t/hello-ryan"
                )
            ]
        )
        response += basiccard
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": "보물상자",
                            "description": "보물상자 안에는 뭐가 있을까",
                            "thumbnail": {
                                "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                            },
                            "buttons": [
                                {
                                    "action": "message",
                                    "label": "열어보기",
                                    "messageText": "짜잔! 우리가 찾던 보물입니다"
                                },
                                {
                                    "action":  "webLink",
                                    "label": "구경하기",
                                    "webLinkUrl": "https://e.kakao.com/t/hello-ryan"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        print(response.get_dict())
        self.assertDictEqual(response.get_dict(), example)

    def test_commerce_card(self):
        response = KakaoResponse()
        card = CommerceCardComponent(
            title="빈티지 목재 보물 상자 (Medium size)",
            description="이 보물 상자 안에는 무엇이 들어있을까요?",
            price=10000,
            discount=1000,
            currency="won",
            thumbnails=[
                Thumbnail(
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg",
                    link=Link(
                        web="https://store.kakaofriends.com/kr/products/1542"
                    )

                )
            ],
            profile=Profile(
                image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4BJ9LU4Ikr_EvZLmijfcjzQKMRCJ2bO3A8SVKNuQ78zu2KOqM",
                nickname="라이언 스토어"
            ),
            buttons=[
                Button(
                    action="webLink",
                    label="구매하기",
                    web_link_url="https://store.kakaofriends.com/kr/products/1542"
                ),
                Button(
                    action="phone",
                    label="전화하기",
                    phone_number="354-86-00070"
                ),
                Button(
                    action="share",
                    label="공유하기"
                )
            ]
        )
        response += card
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "commerceCard": {
                            "title": "빈티지 목재 보물 상자 (Medium size)",
                            "description": "이 보물 상자 안에는 무엇이 들어있을까요?",
                            "price": 10000,
                            "discount": 1000,
                            "currency": "won",
                            "thumbnails": [
                                {
                                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg",
                                    "link": {
                                        "web": "https://store.kakaofriends.com/kr/products/1542"
                                    }
                                }
                            ],
                            "profile": {
                                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4BJ9LU4Ikr_EvZLmijfcjzQKMRCJ2bO3A8SVKNuQ78zu2KOqM",
                                "nickname": "라이언 스토어"
                            },
                            "buttons": [
                                {
                                    "label": "구매하기",
                                    "action": "webLink",
                                    "webLinkUrl": "https://store.kakaofriends.com/kr/products/1542"
                                },
                                {
                                    "label": "전화하기",
                                    "action": "phone",
                                    "phoneNumber": "354-86-00070"
                                },
                                {
                                    "label": "공유하기",
                                    "action": "share"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertDictEqual(response.get_dict(), example)

    def test_list_card(self):
        response = KakaoResponse()
        card = ListCardComponent(
            header=ListItem(
                title="챗봇 관리자센터를 소개합니다."
            ),
            items=[
                ListItem(
                    title="챗봇 관리자센터",
                    description="새로운 AI의 내일과 일상의 변화",
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/img_001.jpg",
                    link=Link(
                        web="https://namu.wiki/w/%EB%9D%BC%EC%9D%B4%EC%96%B8(%EC%B9%B4%EC%B9%B4%EC%98%A4%ED%94%84%EB%A0%8C%EC%A6%88)"
                    )
                ),
                ListItem(
                    title="챗봇 관리자센터",
                    description="카카오톡 채널 챗봇 만들기",
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/img_002.jpg",
                    action="block",
                    block_id="62654c249ac8ed78441532de",
                    extra={
                        "key1": "value1",
                        "key2": "value2"
                    }
                ),
                ListItem(
                    title="Kakao i Voice Service",
                    description="보이스봇 / KVS 제휴 신청하기",
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/img_003.jpg",
                    action="message",
                    message_text="Kakao i Voice Service",
                    extra={
                        "key1": "value1",
                        "key2": "value2"
                    }
                ),
            ],
            buttons=[
                Button(
                    label="구경가기",
                    action="block",
                    block_id="62654c249ac8ed78441532de",
                    extra={
                        "key1": "value1",
                        "key2": "value2"
                    }
                )
            ]
        )
        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": "챗봇 관리자센터를 소개합니다."
                            },
                            "items": [
                                {
                                    "title": "챗봇 관리자센터",
                                    "description": "새로운 AI의 내일과 일상의 변화",
                                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/img_001.jpg",
                                    "link": {
                                        "web": "https://namu.wiki/w/%EB%9D%BC%EC%9D%B4%EC%96%B8(%EC%B9%B4%EC%B9%B4%EC%98%A4%ED%94%84%EB%A0%8C%EC%A6%88)"
                                    }
                                },
                                {
                                    "title": "챗봇 관리자센터",
                                    "description": "카카오톡 채널 챗봇 만들기",
                                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/img_002.jpg",
                                    "action": "block",
                                    "blockId": "62654c249ac8ed78441532de",
                                    "extra": {
                                        "key1": "value1",
                                        "key2": "value2"
                                    }
                                },
                                {
                                    "title": "Kakao i Voice Service",
                                    "description": "보이스봇 / KVS 제휴 신청하기",
                                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/img_003.jpg",
                                    "action": "message",
                                    "messageText": "Kakao i Voice Service",
                                    "extra": {
                                        "key1": "value1",
                                        "key2": "value2"
                                    }
                                }
                            ],
                            "buttons": [
                                {
                                    "label": "구경가기",
                                    "action": "block",
                                    "blockId": "62654c249ac8ed78441532de",
                                    "extra": {
                                        "key1": "value1",
                                        "key2": "value2"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        response += card
        self.assertDictEqual(response.get_dict(), example)

    def test_carousel(self):
        response = KakaoResponse()
        carousel = CarouselComponent()
        carousel.add_item(
            BasicCardComponent(
                title="보물상자",
                description="보물상자 안에는 뭐가 있을까",
                thumbnail=Thumbnail(
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                ),
                buttons=[
                    Button(
                        action="message",
                        label="열어보기",
                        message_text="짜잔! 우리가 찾던 보물입니다"
                    ),
                    Button(
                        action="webLink",
                        label="구경하기",
                        web_link_url="https://e.kakao.com/t/hello-ryan"
                    )
                ]
            )
        )
        carousel.add_item(
            BasicCardComponent(
                title="보물상자2",
                description="보물상자2 안에는 뭐가 있을까",
                thumbnail=Thumbnail(
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                ),
                buttons=[
                    Button(
                        action="message",
                        label="열어보기",
                        message_text="짜잔! 우리가 찾던 보물입니다"
                    ),
                    Button(
                        action="webLink",
                        label="구경하기",
                        web_link_url="https://e.kakao.com/t/hello-ryan"
                    )
                ]
            )
        )
        carousel.add_item(
            BasicCardComponent(
                title="보물상자3",
                description="보물상자3 안에는 뭐가 있을까",
                thumbnail=Thumbnail(
                    image_url="https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                ),
                buttons=[
                    Button(
                        action="message",
                        label="열어보기",
                        message_text="짜잔! 우리가 찾던 보물입니다"
                    ),
                    Button(
                        action="webLink",
                        label="구경하기",
                        web_link_url="https://e.kakao.com/t/hello-ryan"
                    )
                ]
            )
        )

        response += carousel

        example = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type": "basicCard",
                            "items": [
                                {
                                    "title": "보물상자",
                                    "description": "보물상자 안에는 뭐가 있을까",
                                    "thumbnail": {
                                        "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                                    },
                                    "buttons": [
                                        {
                                            "action": "message",
                                            "label": "열어보기",
                                            "messageText": "짜잔! 우리가 찾던 보물입니다"
                                        },
                                        {
                                            "action":  "webLink",
                                            "label": "구경하기",
                                            "webLinkUrl": "https://e.kakao.com/t/hello-ryan"
                                        }
                                    ]
                                },
                                {
                                    "title": "보물상자2",
                                    "description": "보물상자2 안에는 뭐가 있을까",
                                    "thumbnail": {
                                        "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                                    },
                                    "buttons": [
                                        {
                                            "action": "message",
                                            "label": "열어보기",
                                            "messageText": "짜잔! 우리가 찾던 보물입니다"
                                        },
                                        {
                                            "action":  "webLink",
                                            "label": "구경하기",
                                            "webLinkUrl": "https://e.kakao.com/t/hello-ryan"
                                        }
                                    ]
                                },
                                {
                                    "title": "보물상자3",
                                    "description": "보물상자3 안에는 뭐가 있을까",
                                    "thumbnail": {
                                        "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
                                    },
                                    "buttons": [
                                        {
                                            "action": "message",
                                            "label": "열어보기",
                                            "messageText": "짜잔! 우리가 찾던 보물입니다"
                                        },
                                        {
                                            "action":  "webLink",
                                            "label": "구경하기",
                                            "webLinkUrl": "https://e.kakao.com/t/hello-ryan"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }

        self.assertDictEqual(response.get_dict(), example)


if __name__ == '__main__':
    unittest.main()
