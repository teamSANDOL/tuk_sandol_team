"""ibook 파일 다운로드 모듈입니다.

한국공학대학교 iBook에서 파일을 다운로드하는 모듈입니다.
BookDownloader 클래스를 사용하여 iBook에서 파일을 다운로드할 수 있습니다.

Example:
    link = "https://ibook.tukorea.ac.kr/Viewer/menu02"
    downloader = BookDownloader(link)  # BookDownloader 객체 생성
    downloader.get_file("data.xlsx")  # data.xlsx에 파일 저장
"""

import os
import json
from typing import Optional
from xml.etree import ElementTree
import requests

from api_server.settings import logger


class FetchError(Exception):
    """Exception raised when fetching fails."""

    def __init__(self, status_code=None, message="파일 처리중 오류가 발생했습니다."):
        """파일 처리중 오류가 발생했을 때 발생하는 예외입니다."""
        self.status_code = status_code
        self.message = (
            message if status_code is None else f"{message} Status code: {status_code}"
        )
        super().__init__(self.message)


class FetchBookcodeError(FetchError):
    """Exception raised when fetching bookcode fails."""

    def __init__(self, status_code, message="북코드 추출 실패."):
        """북코드 추출 실패 예외입니다."""
        super().__init__(status_code, message)


class FetchFileListError(FetchError):
    """Exception raised when fetching file list fails."""

    def __init__(self, status_code=None, message="파일 목록을 가져오지 못했습니다."):
        """파일 목록을 가져오지 못했을 때 발생하는 예외입니다."""
        super().__init__(status_code, message)


class DownloadFileError(FetchError):
    """Exception raised when downloading file fails."""

    def __init__(self, status_code, message="파일 다운로드 실패."):
        """파일 다운로드 실패 예외입니다."""
        super().__init__(status_code, message)


class BookcodeNotExistError(Exception):
    """북코드가 없을 때 발생하는 예외입니다."""

    def __init__(self, message="북코드가 없습니다."):
        """북코드가 없을 때 발생하는 예외입니다."""
        self.message = message
        super().__init__(self.message)


class BookDownloader:
    """한국공학대학교 iBook에서 파일을 다운로드하는 클래스입니다.

    iBook에서 파일을 다운로드하는 클래스입니다.
    BookDownloader(iBook URL, 파일 목록 URL)로 객체를 생성하고
    get_file(파일 이름) 메소드를 호출하면 파일 이름으로 파일을 다운로드합니다.

    Args:
        url(str): iBook URL
        file_list_url(str): 파일 목록을 가져오는 URL

    Attributes:
        url(str): iBook URL
        file_list_url(str): 파일 목록을 가져오는 URL
        bookcode(str): iBook의 bookcode
        file_list_headers(dict): 파일 목록을 가져올 때 사용하는 HTTP 헤더
        file_name(str): 다운로드할 파일 이름
    """

    def __init__(
        self,
        url="https://ibook.tukorea.ac.kr/Viewer/menu02",
        file_list_url="https://ibook.tukorea.ac.kr/web/RawFileList",
        image_save_path = "images",
    ):
        """ibook 파일 다운로드 모듈입니다."""
        self.url = url
        self.file_list_url = file_list_url
        self.image_save_path = image_save_path
        self.bookcode = None
        self.file_list_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://ibook.tukorea.ac.kr",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
        }
        self.file_name = None

    def check_for_errors(self, response_content: str):
        """서버 응답에서 에러를 감지하고 처리합니다.

        서버 응답에서 에러를 감지하고 처리하는 메소드입니다.
        response_content를 xml로 파싱하고,
        result가 error이면 message를 출력하고 True를 반환합니다.
        그렇지 않으면 False를 반환합니다.

        Args:
            response_content(str): 서버 응답

        Returns:
            bool: 에러가 감지되었는지 여부
        """
        try:
            root = ElementTree.fromstring(response_content)
            result_element = root.find("result")  # result 태그 찾기
            if result_element is None:
                return False  # result 태그가 없으면 에러가 아님\

            # 에러 메시지 출력
            message_element = root.find("message")
            assert message_element is not None  # message 태그가 없으면 에러
            message = message_element.text
            logger.error(f"Error detected: {message}")  # 에러 메시지 출력
            return True
        except ElementTree.ParseError as e:  # xml 파싱 에러
            logger.error(f"Error parsing response: {e}")  # 에러 메시지 출력
        return False

    def fetch_bookcode(self):
        """iBook의 bookcode를 가져오는 메소드입니다.

        iBook의 bookcode를 가져오는 메소드입니다.
        iBook url로 html을 가져와서 bookcode를 찾고,
        self.bookcode에 저장 및 반환합니다.

        Returns:
            str: iBook의 bookcode
            None: bookcode를 찾을 수 없을 때
        """
        response = requests.get(self.url, timeout=10)
        if response.status_code == 200:  # 요청 성공
            lines = response.content.decode("utf-8").split("\n")  # 줄 단위로 분리
            for line in lines:  # 각 줄을 순회하며 bookcode 찾기
                if "var bookcode =" in line:
                    # bookcode 추출
                    bookcode = line.split("=")[1].strip().strip(";").strip("'")
                    self.bookcode = bookcode
                    return self.bookcode  # bookcode 반환
        else:  # 요청 실패
            raise FetchBookcodeError(response.status_code)

    def fetch_file_list(self):
        """파일 목록을 가져오는 메소드입니다.

        파일 목록 URL로 파일 목록을 가져오는 메소드입니다.
        bookcode가 없으면 "Bookcode를 가져오지 못했습니다."를 출력하고 None을 반환합니다.
        파일 목록을 가져오는 요청을 보내고,
        응답이 200이면 파일 목록을 반환합니다.

        Returns:
            str: 파일 목록
            None: 파일 목록을 가져오지 못했을 때
        """
        if self.bookcode is None:
            try:
                self.fetch_bookcode()
            except FetchBookcodeError as error:
                raise BookcodeNotExistError from error   # bookcode가 없으면 에러

        # key는 kpu로 고정(한국공학대학교 iBook의 key: 바뀔 수 있음)
        data = {"key": "kpu", "bookcode": self.bookcode, "base64": "N"}

        # 파일 목록 가져오기
        response = requests.post(
            self.file_list_url, headers=self.file_list_headers, data=data, timeout=10
        )

        # 파일 목록 가져오기 성공
        if response.status_code == 200 and not self.check_for_errors(
            response.content.decode("utf-8")
        ):
            return response.content.decode("utf-8")
        else:  # 파일 목록 가져오기 실패
            raise FetchFileListError(response.status_code)

    def download_file(self, file_url, save_as):
        """파일을 다운로드하는 메소드입니다.

        파일을 다운로드하는 메소드입니다.
        파일 URL로 요청을 보내고,
        응답이 200이면 파일을 저장합니다.
        파일을 저장할 때는 save_as로 지정한 이름으로 저장합니다.

        Args:
            file_url(str): 다운로드할 파일 URL
            save_as(str): 저장할 파일 이름
        """
        # 파일 다운로드
        response = requests.get(file_url, timeout=10)

        # 파일 다운로드 성공
        if response.status_code == 200:
            with open(save_as, "wb") as f:
                f.write(response.content)
            logger.info(f"File saved to {save_as}")
        else:  # 파일 다운로드 실패
            raise DownloadFileError(response.status_code)

    def download_images(self, image_save_path=None):
        """모든 이미지 다운로드
        
        모든 이미지를 다운로드하는 메소드입니다.
        이미지 목록을 가져와서 이미지를 다운로드합니다.
        이미지는 image_save_path에 저장됩니다.

        Args:
            image_save_path(str, optional): 이미지 저장 경로. Defaults to None.
        """
        if image_save_path is None:
            image_save_path = self.image_save_path

        self.fetch_bookcode()
        image_urls = self.fetch_image_list()

        if not image_urls:
            logger.info("다운로드할 이미지가 없습니다.")
            return
        else:
            os.makedirs(image_save_path, exist_ok=True)

        for idx, img_url in enumerate(image_urls, start=1):
            save_as = os.path.join(image_save_path, f"page_{idx}.jpg")
            response = requests.get(img_url, headers=self.file_list_headers, timeout=1)

            if response.status_code == 200:
                with open(save_as, "wb") as f:
                    f.write(response.content)
                logger.info(f"이미지 저장 완료: {save_as}")
            else:
                logger.info(f"다운로드 실패: {img_url}, Status code: {response.status_code}")

    def fetch_image_list(self):
        """JSON에서 이미지 파일 목록을 가져오는 메소드
        
        JSON에서 이미지 파일 목록을 가져오는 메소드입니다.
        이미지 목록을 가져와서 이미지 URL을 추출하고,
        이미지 URL을 반환합니다.

        Returns:
            list: 이미지 URL 목록
        """
        if self.bookcode is None:
            try:
                self.fetch_bookcode()
            except FetchBookcodeError as error:
                raise BookcodeNotExistError from error   # bookcode가 없으면 에러

        json_url = f"{self.url.rsplit('/', 1)[0]}/getBookXML/{self.bookcode}"
        response = requests.get(json_url, headers=self.file_list_headers, timeout=1)

        if response.status_code != 200:
            raise FetchError(response.status_code, "이미지 목록을 가져오지 못했습니다.")

        try:
            image_data = json.loads(response.text)
            image_links = ["https:" + img["src"].replace("\\/", "/") for img in image_data]
            return image_links
        except json.JSONDecodeError as e:
            raise FetchError(None, f"JSON 파싱 오류: {e}") from e

    def get_file_url(self, file_list_content: str):
        """file_list_content에서 파일 URL을 가져오는 메소드입니다.

        file_list_content에서 파일 URL을 가져오는 메소드입니다.
        file_list_content를 xml로 파싱하고,
        root에서 file 태그를 찾아서 파일 이름과 파일 URL을 가져옵니다.
        파일 URL이 없으면 host와 bookcode를 이용해 URL을 생성합니다.

        Args:
            file_list_content(str): 파일 목록 xml

        Returns:
            str: 추출되거나 생성된 파일 URL
        """
        root = ElementTree.fromstring(file_list_content)
        for file in root.findall("file"):
            # 파일 이름 가져오기
            file_name = file.attrib["name"]
            self.file_name = file_name

            # 파일 URL 가져오기
            file_url = file.attrib.get("file_url", None)
            if file_url:
                return file_url

            # 파일 URL이 없으면 host와 Bookcode를 이용해 URL 생성
            host = file.attrib["host"]
            bookcode = root.attrib["bookcode"]

            # 파일 URL 생성(한국공학대학교 iBook의 파일 URL 형식)
            file_url = (
                f"https://{host}/contents/{bookcode[0]}/{bookcode[:3]}"
                f"/{bookcode}/raw/{file_name}"
            )
            return file_url

    def get_file(self, file_name: Optional[str] = None):
        """Book 파일을 다운로드하는 메소드입니다.

        book 파일을 다운로드하는 메소드입니다.
        bookcode를 가져오고,
        파일 목록을 가져와서 파일 URL을 추출하거나 생성합니다.
        파일 이름이 주어지지 않으면 self.file_name을 사용합니다.
        이후 파일 이름으로 파일을 다운로드해 저장합니다.

        Args:
            file_name(str, optional): _description_. Defaults to None.
        """
        # 파일 이름이 주어지지 않으면 self.file_name 사용
        file_name = file_name or self.file_name

        self.fetch_bookcode()  # bookcode 가져오기

        # bookcode가 있으면 파일 목록 가져오기
        if self.bookcode:
            file_list_content = self.fetch_file_list()  # 파일 목록 가져오기
            if file_list_content:  # 파일 목록이 있으면 파일 다운로드
                file_url = self.get_file_url(file_list_content)
                self.download_file(file_url, file_name)

if __name__ == "__main__":
    # 사용 예시
    bus_link = "https://ibook.tukorea.ac.kr/Viewer/bus01"
    downloader = BookDownloader()  # BookDownloader(bus_link) 로 셔틀 버스 파일 다운로드
    downloader.get_file("data.xlsx")  # data.xlsx에 파일 저장
    downloader.download_images()  # 이미지 다운로드
    bus_image = BookDownloader(bus_link)
    bus_image.fetch_bookcode()
    print(bus_image.fetch_image_list())  # 이미지 다운로드
