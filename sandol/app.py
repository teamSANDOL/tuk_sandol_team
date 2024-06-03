from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from api_server.meal import meal_api
from api_server.utils import error_message
from api_server.kakao.response import KakaoResponse

app = FastAPI()
app.include_router(meal_api)

@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        KakaoResponse().add_component(error_message(exc)).get_dict()
    )

@app.get("/")
async def root():
    return {"test": "Hello Sandol"}

handler = Mangum(app)
