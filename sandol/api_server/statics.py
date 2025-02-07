from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from kakao_chatbot import Payload
from kakao_chatbot.response import (
    KakaoResponse,
)
from kakao_chatbot.response.components import (
    SimpleTextComponent,
    SimpleImageComponent,
)

from api_server.utils import (
    parse_payload,
    create_openapi_extra,
    make_org_group_list,
    make_unit_item,
)
from api_server.settings import logger
from crawler import get_shuttle_images
from crawler.university_structure import (
    UniversityStructure,
    OrganizationGroup,
    get_tukorea_structure,
)

statics_router = APIRouter(prefix="/statics")


@statics_router.post(
    "/info",
    openapi_extra=create_openapi_extra(
        detail_params={
            "organization": {
                "origin": "컴공",
                "value": "컴퓨터공학부",
            },
        },
        utterance="컴공 정보",
    ),
)
def info(payload: Payload = Depends(parse_payload)):
    """학교 조직정보를 반환합니다.
    
    조직이 하위 조직을 갖는경우 조직의 리스트를,
    하위 조직이 없는 경우 조직의 정보를 반환합니다. 

    ## 카카오 챗봇  연결 정보
    ---
    - 동작방식: 발화

    - OpenBuilder:
        - 블럭: "정보 검색"
        - 스킬: "정보 검색"
    
    - Params:
        - detail_params:
            organization(조직): 컴퓨터공학부
    ---
    
    Returns:
        JSONResponse: 학교 조직 정보
    """
    org = payload.action.params.get("organization", None)
    if org is None:
        org = "대표연락처"
    tukorea: UniversityStructure = get_tukorea_structure()
    unit = tukorea.get_unit(org)

    response = KakaoResponse()
    if unit is None:
        response.add_component(SimpleTextComponent("해당 조직을 찾을 수 없습니다."))
        return JSONResponse(response.get_dict())

    if isinstance(unit, OrganizationGroup):
        response.add_component(make_org_group_list(unit))
    else:
        response.add_component(make_unit_item(unit))
    return JSONResponse(response.get_dict())

@statics_router.post(
    "/unit_info",
    openapi_extra=create_openapi_extra(
        client_extra={
            "name": "컴퓨터공학부",
            "phone": "03180410510",
        }
    ),
)
def unit_info(payload: Payload = Depends(parse_payload)):
    """학교 조직 정보를 반환합니다.

    Client Extra에 있는 정보를 기반으로 학교 조직 정보를 반환합니다.

    ## 카카오 챗봇  연결 정보
    ---
    - 동작방식: 버튼 연결

    - OpenBuilder:
        - 블럭: "조직 정보"
        - 스킬: "조직 정보"
    
    - Params:
        - client_extra:
            name: 컴퓨터공학부
            phone: 03180410510
    ---

    Returns:
        JSONResponse: 학교 조직 정보
    """
    response = KakaoResponse()
    response.add_component(make_unit_item(payload.action.client_extra))
    return JSONResponse(response.get_dict())

@statics_router.post(
    "/shuttle_info",
    openapi_extra=create_openapi_extra(
        utterance="셔틀버스",
    ),
)
def shuttle_info():
    """셔틀버스 정보를 반환합니다.

    ## 카카오 챗봇  연결 정보
    ---
    - 동작방식: 발화

    - OpenBuilder:
        - 블럭: "셔틀버스 정보"
        - 스킬: "셔틀버스 정보"
    ---

    Returns:
        JSONResponse: 셔틀버스 정보
    """
    shuttle_images = get_shuttle_images()

    response = KakaoResponse()
    for image in shuttle_images:
        response.add_component(SimpleImageComponent(image, "셔틀버스 정보 사진"))
    return JSONResponse(response.get_dict())
