from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base_crawler import BaseCrawler

class WoowaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://career.woowahan.com")

        # 배달의민족 인턴 공고 URL
        self.job_url = f"{self.base_url}/?jobCodes=&employmentTypeCodes=BA002003&serviceSectionCodes=&careerPeriod=&keyword=&category=jobGroupCodes%3ABA005001#recruit-list"

    def get_html_selenium(self, url, wait_selector):
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
            # 페이지가 로드될 때까지 대기 (최대 5초)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".recruit-type-list")))
            html = driver.page_source
        except:
            print(f"⚠️ {url}에서 데이터를 찾을 수 없습니다. (빠르게 종료)")
            html = None  # 공고가 없을 경우 None 반환

        driver.quit()
        return html

    def parse_list_page(self, html):
        """ 배달의민족 인턴 공고 목록을 크롤링하는 함수 """
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환

        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        job_elements = soup.select(".recruit-type-list li a.title")  # 모든 공고 항목 가져오기

        if not job_elements:
            print("⚠️ 배달의민족 인턴 공고가 존재하지 않습니다.")
            return []  # 공고가 없으면 빈 리스트 반환

        for a_tag in job_elements:
            employment_type = a_tag.select_one(".flag-type span")  # "정규직", "인턴" 등 정보
            if not employment_type or "인턴" not in employment_type.text:
                continue  # 인턴 공고가 아니면 스킵

            href_value = a_tag.get("href")  # 🔹 href 값 가져오기
            if not href_value:
                continue  # href 값이 없으면 스킵

            # 🔹 공고 URL 생성 (base_url 결합)
            notice_url = f"{self.base_url}{href_value.split('?')[0]}"  # ✅ '?뒤의 파라미터' 제거

            # 🔹 공고 제목 가져오기
            title_tag = a_tag.select_one("p.fr-view")
            notice_title = title_tag.text.strip() if title_tag else "제목 없음"

            # 🔹 모집 기간 가져오기 (없을 수도 있음)
            notice_period = a_tag.select_one(".flag-type span:nth-child(2)")
            notice_period = notice_period.text.strip() if notice_period else "정보 없음"

            # 🔹 딕셔너리 형태로 저장
            job_links.append({
                "notice_url": notice_url,
                "title": notice_title,
                "period": notice_period,
            })

        return job_links

    def crawl(self):
        """ 배달의민족 인턴 공고 리스트 크롤링 """
        print("🛠️ 배달의민족 인턴 공고 크롤링 중...")
        html = self.get_html_selenium(self.job_url, ".recruit-type-list")
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환
        return self.parse_list_page(html)
