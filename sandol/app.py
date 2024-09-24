"""Sandol의 메인 애플리케이션 파일입니다."""
from fastapi import FastAPI, HTTPException, Request, status  # noqa: F401 # pylint: disable=W0611
from fastapi.responses import JSONResponse  # noqa: F401
from mangum import Mangum
from kakao_chatbot.response import KakaoResponse
import uvicorn

from api_server.meal import meal_api
from api_server.utils import error_message


app = FastAPI()
app.include_router(meal_api)


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):  # pylint: disable=W0613
    return JSONResponse(
        KakaoResponse().add_component(error_message(exc)).get_dict()
    )


@app.get("/")
async def root():
    return {"test": "Hello Sandol"}

handler = Mangum(app)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5600, reload=True)
