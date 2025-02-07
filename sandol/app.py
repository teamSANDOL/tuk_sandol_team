"""Sandol의 메인 애플리케이션 파일입니다."""

import traceback

from fastapi import FastAPI, HTTPException, Request, status, Depends  # noqa: F401 # pylint: disable=W0611
from fastapi.responses import JSONResponse  # noqa: F401
from kakao_chatbot import Payload
from kakao_chatbot.response import KakaoResponse
from kakao_chatbot.response.components import SimpleTextComponent
import uvicorn

from api_server.settings import logger
from api_server.meal import meal_api
from api_server.statics import statics_router
from api_server.utils import error_message, parse_payload


app = FastAPI(root_path="/api")
app.include_router(meal_api)
app.include_router(statics_router)




@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):
    # 예외 처리 시 로그 남기기
    logger.error(
        "Exception occurred: %s\n%s"
        % (exc, "".join(traceback.format_tb(exc.__traceback__)))
    )
    return JSONResponse(KakaoResponse().add_component(error_message(exc)).get_dict())


@app.get("/")
async def root():
    """루트 엔드포인트입니다."""
    logger.info("Root endpoint accessed")
    return {"test": "Hello Sandol"}


@app.post("/get_id")
async def get_id(payload: Payload = Depends(parse_payload)):
    """사용자의 ID를 반환하는 엔드포인트입니다."""
    logger.info("Get ID endpoint accessed")
    logger.debug(f"User ID: {payload.user_id}")
    response = KakaoResponse()
    response.add_component(SimpleTextComponent(payload.user_id))
    return JSONResponse(response.get_dict())


if __name__ == "__main__":
    logger.info("Starting Sandol server")
    uvicorn.run("app:app", host="0.0.0.0", port=5600, reload=True)
