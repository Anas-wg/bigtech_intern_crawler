from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from .base_crawler import BaseCrawler

class DaangnCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://about.daangn.com/jobs")

        # 🔹 크롤링할 직군별 인턴 공고 페이지 URL 리스트
        self.job_urls = {
            "Frontend": f"{self.base_url}/software-engineer-frontend/?etype=INTERN#_filter",
            "Backend": f"{self.base_url}/software-engineer-backend/?etype=INTERN#_filter",
            "iOS": f"{self.base_url}/software-engineer-ios/?etype=INTERN#_filter",
            "Machine Learning": f"{self.base_url}/software-engineer-machine-learning/?etype=INTERN#_filter",
        }

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
            # **📌 공고 리스트 존재 여부 빠르게 확인 (2초)**
            WebDriverWait(driver, timeout=2, poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".c-bQzyIt .c-jpGEAj li a"))
            )

            # **📌 공고가 없으면 빠르게 종료**
            if not driver.find_elements(By.CSS_SELECTOR, ".c-bQzyIt .c-jpGEAj li a"):
                print(f"⚠️ {url}에서 공고를 찾을 수 없습니다. (빠르게 종료)")
                driver.quit()
                return None

            # **📌 공고가 있으면 본격 크롤링 (최대 5초)**
            WebDriverWait(driver, timeout=5, poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".c-bQzyIt"))
            )
            html = driver.page_source

        except TimeoutException:
            print(f"⚠️ {url}에서 공고를 찾을 수 없습니다. (빠르게 종료)")
            html = None  # 공고 없음 즉시 반환

        finally:
            driver.quit()
        
        return html

    def parse(self, html):
        """ 당근마켓 인턴 공고를 크롤링하는 함수 """
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환

        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        job_elements = soup.select(".c-bQzyIt .c-jpGEAj li a")  # 모든 공고 항목 가져오기

        if not job_elements:
            print("⚠️ 당근마켓 인턴 공고가 존재하지 않습니다.")
            return []  # 공고가 없으면 빈 리스트 반환

        for a_tag in job_elements:
            href_value = a_tag.get("href")
            if not href_value:
                continue  # href 값이 없으면 스킵

            # 🔹 공고 URL 생성
            notice_url = f"https://about.daangn.com{href_value}"

            # 🔹 공고 제목 가져오기
            title_tag = a_tag.select_one("h3.c-boyXyq")
            notice_title = title_tag.text.strip() if title_tag else "제목 없음"

            # 🔹 딕셔너리 형태로 저장
            job_links.append({
                "notice_url": notice_url,
                "title": notice_title,
                "period": "정보 없음"
            })

        return job_links

    def crawl(self):
        """ 당근마켓 인턴 공고 리스트 크롤링 """
        all_jobs = []

        for category, url in self.job_urls.items():
            print(f"🛠️ {category} 인턴 공고 크롤링 중...")

            html = self.get_html_selenium(url)

            if html:
                jobs = self.parse(html)
                all_jobs.extend(jobs)

        return all_jobs
