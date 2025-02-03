from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base_crawler import BaseCrawler

class LineCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://careers.linecorp.com")

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
            # 공고 리스트가 렌더링될 때까지 기다림 (최대 10초)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".job_list")))
            html = driver.page_source
        except:
            print("⚠️ LINE 인턴 공고가 존재하지 않습니다.")
            html = None  # 공고가 없을 경우 None 반환

        driver.quit()
        return html

    def parse(self, html):
        """ LINE 채용 공고를 크롤링하는 함수 (인턴 공고 전용) """
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환

        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        job_elements = soup.select(".job_list > li > a")  # 모든 공고 항목 가져오기

        if not job_elements:
            print("⚠️ LINE 인턴 공고가 존재하지 않습니다.")
            return []  # 공고가 없으면 빈 리스트 반환

        for a_tag in job_elements:
            href_value = a_tag.get("href")
            if not href_value:
                continue  # href 값이 없으면 스킵

            # 🔹 공고 URL 생성
            notice_url = self.base_url + href_value

            # 🔹 공고 제목 가져오기
            title_tag = a_tag.select_one("h3.title")
            notice_title = title_tag.text.strip() if title_tag else "제목 없음"

            # 🔹 모집 기간 가져오기
            date_tag = a_tag.select_one(".date")
            notice_period = date_tag.text.strip() if date_tag else "기간 정보 없음"

            # 🔹 딕셔너리 형태로 저장
            job_links.append({
                "notice_url": notice_url,
                "title": notice_title,
                "period": notice_period
            })

        return job_links

    def crawl(self):
        """ LINE 인턴 채용 공고 리스트 크롤링 """
        url = f"{self.base_url}/ko/jobs?ca=Engineering&ty=Intern"
        html = self.get_html_selenium(url)  # Selenium으로 동적 렌더링된 HTML 가져오기
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환
        return self.parse(html)
