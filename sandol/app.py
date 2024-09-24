"""Sandol의 메인 애플리케이션 파일입니다."""
import traceback

from fastapi import FastAPI, HTTPException, Request, status  # noqa: F401 # pylint: disable=W0611
from fastapi.responses import JSONResponse  # noqa: F401
from mangum import Mangum
from kakao_chatbot.response import KakaoResponse
import uvicorn

from api_server.settings import logger
from api_server.meal import meal_api
from api_server.utils import error_message


app = FastAPI()
app.include_router(meal_api)


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):  # pylint: disable=W0613
    # 예외 처리 시 로그 남기기
    logger.error(
        "Exception occurred: %s\n%s" % (exc, "".join(traceback.format_tb(exc.__traceback__)))
        )
    return JSONResponse(
        KakaoResponse().add_component(error_message(exc)).get_dict()
    )


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"test": "Hello Sandol"}

handler = Mangum(app)


if __name__ == "__main__":
    logger.info("Starting Sandol server")
    uvicorn.run("app:app", host="0.0.0.0", port=5600, reload=True)
