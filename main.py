"""테스트 서버를 실행시키기 위한 파일입니다."""
from sandol.app import app  # noqa
import uvicorn

if __name__ == "__main__":
    uvicorn.run("sandol.app:app", host="0.0.0.0", port=5600, reload=True)
