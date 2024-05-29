"""Sandol의 메인 애플리케이션 파일입니다."""
from fastapi import FastAPI, HTTPException, Request, status  # noqa: F401 # pylint: disable=W0611
from fastapi.responses import JSONResponse  # noqa: F401

from .api_server.meal import meal_api
from .api_server.utils import error_message
from .api_server.kakao.response import KakaoResponse


app = FastAPI()
app.include_router(meal_api)


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):  # pylint: disable=W0613
    return JSONResponse(
        KakaoResponse().add_component(error_message(exc)).get_dict()
    )


@app.get("/")
async def root():
    """루트 페이지입니다."""
    return "Hello Sandol"
