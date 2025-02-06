from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base_crawler import BaseCrawler

class TossCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://toss.im/career/jobs?employment_type=%EC%B4%88%EB%8B%A8%EA%B8%B0%EA%B3%84%EC%95%BD%EC%A7%81%2C%EB%8B%A8%EA%B8%B0%EA%B3%84%EC%95%BD%EC%A7%81%2C%EA%B3%84%EC%95%BD%EC%A7%81&category=Backend%2CFrontend%2CInfra%2CQA%2CFull%20Stack%2CApp%2CEngineering")

    def get_html_selenium(self, url):
        """ Selenium을 사용하여 JavaScript가 렌더링된 HTML을 가져오는 함수 """
        options = webdriver.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"  # Chrome 실행 경로 지정
        options.add_argument("--headless")  # GUI 없이 실행
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        try:
            # 🔹 공고 리스트가 렌더링될 때까지 기다림 (최대 3초로 변경)
            WebDriverWait(driver, 3).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, ".css-16ht878")  # 요소가 존재하면 바로 반환
            )
            html = driver.page_source
        except:
            print(f"⚠️ {url}에서 토스 인턴 공고를 찾을 수 없습니다. (빠르게 종료)")
            html = None  # 공고가 없을 경우 None 반환

        driver.quit()
        return html


    def parse(self, html):
        """ 토스 인턴 공고를 크롤링하는 함수 """
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환

        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        job_elements = soup.select(".css-g65o95")  # 모든 공고 항목 가져오기

        if not job_elements:
            print("⚠️ 토스 인턴 공고가 존재하지 않습니다.")
            return []  # 공고가 없으면 빈 리스트 반환

        for job in job_elements:
            href_value = job.get("href")
            if not href_value:
                continue  # href 값이 없으면 스킵

            # 🔹 공고 URL 생성
            notice_url = f"https://toss.im{href_value}"

            # 🔹 공고 제목 가져오기
            title_tag = job.select_one("span.typography.typography--h5")
            notice_title = title_tag.text.strip() if title_tag else "제목 없음"

            # # 🔹 공고 설명 가져오기
            # description_tag = job.select_one("div.css-8444y9")
            # notice_description = description_tag.text.strip() if description_tag else "설명 없음"

            # 🔹 딕셔너리 형태로 저장
            job_links.append({
                "notice_url": notice_url,
                "title": notice_title,
                "period": "정보 없음"
            })

        return job_links

    def crawl(self):
        """ 토스 인턴 공고 리스트 크롤링 """
        print("🛠️ 토스 인턴 공고 크롤링 중...")
        html = self.get_html_selenium(self.base_url)
        if html:
            jobs = self.parse(html)
            return jobs
        return []
