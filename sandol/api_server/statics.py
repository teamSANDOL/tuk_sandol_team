from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from kakao_chatbot import Payload
from kakao_chatbot.response import (
    KakaoResponse,
)
from kakao_chatbot.response.components import (
    SimpleTextComponent,
)

from api_server.utils import (
    parse_payload,
    create_openapi_extra,
    make_org_group_list,
    make_unit_item,
)
from api_server.settings import logger
from crawler.university_structure import (
    UniversityStructure,
    OrganizationGroup,
    get_tukorea_structure,
)

statics_router = APIRouter(prefix="/statics")


@statics_router.post(
    "/phone",
    openapi_extra=create_openapi_extra(
        detail_params={
            "organization": {
                "origin": "컴공",
                "value": "컴퓨터공학부",
            },
        },
        utterance="전화 컴공",
    ),
)
def phone(payload: Payload = Depends(parse_payload)):
    """학교 전화번호를 반환합니다."""
    org = payload.action.params.get("organization", None)
    if org is None:
        org = "대표전화"
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
        },
        utterance="컴공 정보",
    ),
)
def unit_info(payload: Payload = Depends(parse_payload)):
    """학교 조직 정보를 반환합니다."""
    response = KakaoResponse()
    response.add_component(make_unit_item(payload.action.client_extra))
    return JSONResponse(response.get_dict())
