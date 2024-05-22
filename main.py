"""테스트 서버를 실행시키기 위한 파일입니다."""
from sandol.app import app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)
