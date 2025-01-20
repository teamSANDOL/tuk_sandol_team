# 산돌이 프로젝트 개발 문서

## 개요
산돌이는 **FastAPI** 기반으로 개발된 학국공학대학교 관련 정보 제공 챗봇 서비스입니다. 사용자는 카카오톡 채널을 통해 학국공학대학교 정보를 확인하고 식당 등록, 메뉴 관리 등의 서비스를 이용할 수 있습니다. 이 문서는 새로운 개발자가 프로젝트를 이해하고 기여할 수 있도록 프로젝트 구조, 주요 기능, 환경 설정, 및 실행 방법 등을 상세히 설명합니다.

---

## 프로젝트 구조
프로젝트는 다음과 같은 디렉터리와 파일로 구성되어 있습니다:

```
tuk_sandol_team/
│
├── sandol/
│   ├── api_server/
│   │   ├── __init__.py
│   │   ├── meal.py           # 학식 관련 API 구현
│   │   ├── settings.py       # 환경 설정 및 로깅
│   │   ├── utils.py          # 유틸리티 함수
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_app.py   # API 테스트
│   │
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── cafeteria.py      # 식당 데이터 관리
│   │   ├── ibookcrawler.py   # 학식 데이터 처리
│   │   └── data/             # 학식 데이터 저장
│   │
│   ├── tests/                # 전체 테스트
│   ├── app.py                # FastAPI 애플리케이션 메인 파일
│   ├── Dockerfile            # 도커 설정 파일
│   ├── docker-compose.yml    # 도커 컴포즈 설정
│   ├── requirements.txt      # 의존성 관리
│   └── __init__.py
│
└── tmp/                      # 임시 파일
```

---

## 주요 파일 및 기능

### 1. `app.py`
- **설명**: FastAPI 애플리케이션의 진입점입니다.
- **주요 기능**:
  - 루트 엔드포인트 (`GET /`) - 간단한 상태 확인
  - 사용자 ID 반환 엔드포인트 (`POST /get_id`)

### 2. `meal.py`
- **설명**: 학식 관련 API를 구현합니다.
- **주요 엔드포인트**:
  - `/meal/register/restaurant`: 식당 등록
  - `/meal/register/delete/{meal_type}`: 메뉴 삭제
  - `/meal/view`: 학식 정보 조회
  - `/meal/submit`: 식단 확정

### 3. `cafeteria.py`
- **설명**: 식당 객체를 관리하는 클래스와 관련 메서드를 정의합니다.
- **주요 클래스**:
  - `Restaurant`: 식당 데이터 관리 (등록, 수정, 삭제)
  - `get_meals()`: JSON 파일로부터 식당 정보를 로드하여 객체로 반환

### 4. `ibookcrawler.py`
- **설명**: 학식 데이터를 가공하는 모듈입니다.
- **주요 클래스**:
  - `BookTranslator`: 학식 데이터를 `data.xlsx` 파일에서 추출하여 가공 후 저장

---

## 환경 설정

### 1. `requirements.txt`
필요한 Python 패키지 목록:
- FastAPI
- uvicorn
- pandas
- kakao-chatbot 등

### 2. `docker-compose.yml`
- 서비스 이름: `sandol`
- 데이터 디렉터리 `/tmp/sandol/data`를 컨테이너의 `/app/crawler/data`에 마운트

---

## 실행 방법

### 1. 로컬 환경에서 실행
- python 3.11 버전을 사용합니다.
로컬 환경은 개발 IDE의 linting 등의 기능을 위한 목적으로 사용합니다.
서버의 실행은 Docker 컨테이너를 통해 진행합니다.
```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python app.py
```

### 2. 도커를 이용한 실행
- Docker 컨테이너를 이용하여 애플리케이션을 실행합니다.
도커 컴포즈를 이용하여 실행합니다.
volume을 이용하여 데이터를 저장하고 관리하며, 
`/tmp/sandol/data` 디렉터리와 컨테이너의 `/app/crawler/data` 디렉터리를 연결하여
동기화 하기 때문에, test 환경에서는 해당 연결 경로를 직접 수정하거나,
`/tmp/sandol/data` 디렉터리를 직접 생성하여 사용해야 합니다.
```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up --build
```

### 3. API 테스트
- API 테스트는 `tests/` 디렉터리에 작성된 코드로 실행 가능합니다. 현재까지는 작성되지 않았습니다.
```bash
pytest
```
대신, Swagger UI를 이용하여 API를 테스트할 수 있습니다.
- `http://localhost:8000/docs`로 접속하여 API를 테스트합니다.
이때, localhost 대신 사용하는 서버의 IP 주소를 입력해야 합니다.
---

## 추가 참고 사항

### 데이터 저장 구조
- 학식 데이터는 JSON 파일(`data/test.json`)로 저장됩니다.
- 학식 데이터는 `Restaurant` 클래스와 `BookTranslator` 클래스에서 관리됩니다.

### 로그 관리
- 모든 주요 이벤트는 `api_server/settings.py`에 정의된 로깅 설정을 통해 기록됩니다.

### 에러 처리
- FastAPI 전역 예외 처리기가 구현되어 있어 모든 예외 상황을 JSON 형태로 반환합니다.

---

## 기여 가이드
1. 새로운 기능을 추가하거나 수정할 경우 테스트 코드를 작성해주세요.
2. 모든 PR(Pull Request)은 코드 리뷰를 거쳐야 합니다.
3. 코드 스타일은 [Google Python Style](https://yosseulsin-job.github.io/Google-Python-Style-Guide-kor/)을 준수해주세요. [영어 원문](https://google.github.io/styleguide/pyguide.html)