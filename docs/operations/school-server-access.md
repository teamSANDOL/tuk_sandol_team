# 학교 서버 요청 목록과 접근 제한 대응

산돌이 서비스가 학교(한국공학대학교) 서버로 보내는 요청을 모았다. 학교 보안 개선 뒤 예전 파일 목록 API가 막혔고, 지금은 학교 공식 뷰어와 같은 경로를 쓴다. 막힌 곳에 계속 요청하면 해킹 시도나 업무 방해로 오해받을 수 있으므로 아래 원칙을 지킨다.

## 원칙

- 학교 공식 웹 페이지가 방문자 브라우저에서 스스로 부르는 공개 요청만 쓴다. 비공개 관리 기능, 로그인이 필요한 기능은 쓰지 않는다.
- 401·403·429를 받은 요청은 다시 보내지 않는다. 헤더 위조, 쿠키·토큰 재사용, IP 변경 같은 우회는 하지 않는다. User-Agent도 브라우저로 꾸미지 않는다.
- 학교 서버 상태를 확인할 때는 엔드포인트마다 한 번만 요청한다. 재시도하거나 반복 측정하지 않는다.
- 호출 빈도는 사람이 페이지를 여는 수준보다 낮게 유지한다. 새 크롤러나 수집 주기를 추가하기 전에 이 문서의 표를 갱신한다.
- 학교 응답에 개인정보가 들어 있을 수 있다(열람실 좌석). 이런 본문은 저장하거나 로그에 남기지 않는다.

## 요청 목록 (2026-11-24 확인, 엔드포인트마다 1회)

| 서비스 | 요청 | 용도 | 호출 주기 | 결과 |
|---|---|---|---|---|
| (폐지) | `POST ibook.tukorea.ac.kr/web/RawFileList` | 예전 파일 목록 API | 쓰지 않음 | **403** |
| meal-service, static-info | `POST ibook.tukorea.ac.kr/Viewer/rawFileList` | 식단·셔틀 원본 파일 목록. 공식 뷰어(ext-01.js)가 페이지를 열 때 부르는 요청 | meal 30분 cron(엑셀이 아니면 6시간 건너뜀), static-info 6시간 cron과 수동 refresh | 200 |
| meal-service, static-info | `GET ibook.tukorea.ac.kr/Viewer/menu02`, `/Viewer/bus01` | bookcode 조회, 세션 쿠키 | 위 동기화와 이미지 API 호출 때 | 200 |
| static-info | `GET ibook.tukorea.ac.kr/Viewer/getBookXML/{bookcode}` | 식단표·셔틀 페이지 이미지 목록 | `/static-info/bus`, `/static-info/meal` 요청 때 | 200 |
| meal-service, static-info, 앱 사용자 | `GET contents.tukorea.ac.kr/contents/...` | 원본 파일과 페이지 이미지 | 파일이 바뀌었을 때, 사용자 열람 때 | 200 |
| notice-notification | `GET ibook.kpu.ac.kr/Viewer/bus01` (ibook.tukorea.ac.kr로 이동) | 셔틀 이미지 크롤링(puppeteer) | 1시간 | 200 |
| notice-notification | `GET www.tukorea.ac.kr/tukorea/7607/subview.do`와 글 상세 | 학교 공지 크롤링 | 크롤러 주기 | 200 |
| notice-notification | `GET dorm.tukorea.ac.kr/dorm/2630/subview.do`와 글 상세 | 기숙사 공지 크롤링 | 크롤러 주기 | 200 |
| studyroom-service | `GET smart.tukorea.ac.kr/library2014/Library_Seat_Count.php` | 열람실 좌석 수 | 3분 수집과 실시간 조회(캐시 20초) | 200 |
| studyroom-service | `GET smart.tukorea.ac.kr/library2014/getSeatInfoSql.php` | 열람실 좌석 배치 | 위와 같음 | 200 |

`school_info.json`의 학교 링크와 카카오 봇의 `WEEKLY_MENU_URL`은 사용자에게 보여 주는 주소라 서버가 요청하지 않는다. studyroom의 `LIBRARY_BASE_URL`은 설정만 있고 쓰는 코드가 없다.

### 예전 API가 막힌 경위

- 예전 코드는 `POST /web/RawFileList`(`key=kpu`)로 파일 목록을 받았다. 테스트 서버와 개발 PC 모두 403이었고, 세션 쿠키를 붙여도 같았다.
- 공개된 뷰어 스크립트 `/system/javascript/viewer2/ext/01/ext-01.js`를 보면 지금 공식 뷰어는 `POST /Viewer/rawFileList`(`bookcode`, `base64=N`)를 쓴다. 뷰어 페이지를 연 세션으로 한 번 요청해 200과 파일 목록 XML을 확인했다.
- 뷰어 페이지의 `rawdownloadable` 값이 `true`라서 원본 파일 내려받기는 학교가 공개한 기능이다.

## 코드에 걸어 둔 제약

meal-service(`app/services/ibook_downloader.py`)와 static-info(`app/utils/ibookdownloader.py`)의 `BookDownloader`:

1. 파일 목록은 `/Viewer/rawFileList`로 받는다. 뷰어 GET과 같은 HTTP 클라이언트(쿠키 유지)로 보내고, User-Agent는 `sandol-<서비스명>`으로 밝힌다.
2. **차단 래치**: iBook 요청이 401·403·429를 받으면 그 종류(뷰어, 파일 목록, 이미지 목록, 다운로드)의 요청을 프로세스가 재시작될 때까지 다시 보내지 않는다. 재시도 로직은 없다.
3. 호출부는 차단 예외가 나면 경고 로그만 남기고 건너뛴다. static-info의 셔틀 수동 동기화 API는 이때 503을 돌려준다.
4. meal-service: 식단 원본이 엑셀이 아니면(2026-11 기준 PDF) 내려받지 않고 6시간 동안 다시 조회하지 않는다. 식단 PDF 파싱은 하지 않는다.

## 차단됐을 때

래치가 걸리면 로그에 error가 한 번 남는다. 원인을 확인하기 전에는 컨테이너를 재시작하지 않는다(재시작하면 래치가 풀린다). 학교 뷰어 페이지가 바뀌었는지 공개 스크립트로 먼저 확인하고, 필요하면 학교에 문의한다.
