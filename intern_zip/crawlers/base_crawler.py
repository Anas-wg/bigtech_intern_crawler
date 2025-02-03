# crawlers/base_crawler.py
import requests
from bs4 import BeautifulSoup

class BaseCrawler:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    def __init__(self, base_url):
        self.base_url = base_url

    def get_html(self, url):
        """ 주어진 URL의 HTML을 가져오는 함수 """
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}, Status Code: {response.status_code}")
            return None

    def parse(self, html):
        """ 크롤링한 HTML을 파싱하는 함수 (각 크롤러에서 오버라이드) """
        raise NotImplementedError("Subclasses should implement this method")
