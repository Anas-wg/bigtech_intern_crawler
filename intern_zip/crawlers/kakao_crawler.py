from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from .base_crawler import BaseCrawler

class KakaoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://careers.kakao.com")

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
            # **📌 공고 리스트가 있는지 3초만 대기**
            WebDriverWait(driver, timeout=3, poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".list_jobs"))
            )

            # **📌 공고 리스트 존재 여부 확인**
            if not driver.find_elements(By.CSS_SELECTOR, ".list_jobs > a"):
                print("⚠️ 공고가 존재하지 않습니다. (빠르게 종료)")
                driver.quit()
                return None  # 공고 없음 즉시 반환

            html = driver.page_source

        except TimeoutException:
            print("⚠️ 공고가 존재하지 않습니다. (빠르게 종료)")
            html = None  # 공고 없음 즉시 반환

        finally:
            driver.quit()
        
        return html

    def parse(self, html):
        """ 카카오 채용 공고를 크롤링하는 함수 """
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환

        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        job_elements = soup.select(".list_jobs > a")  # 모든 공고 항목 가져오기

        if not job_elements:
            print("⚠️ 공고가 존재하지 않습니다.")
            return []  # 공고가 없으면 빈 리스트 반환

        for a_tag in job_elements:
            href_value = a_tag.get("href")
            if not href_value:
                continue  # href 값이 없으면 스킵

            # 🔹 공고 URL 생성
            notice_url = self.base_url + href_value.split("?")[0]

            # 🔹 공고 제목 가져오기
            title_tag = a_tag.select_one(".area_info .wrap_info span h4")
            notice_title = title_tag.text.strip() if title_tag else "제목 없음"

            # 🔹 모집 기간 가져오기
            notice_period = None
            for dt, dd in zip(a_tag.select(".list_info dt"), a_tag.select(".list_info dd")):
                if dt.text.strip() == "영입마감일":  # "모집 기간" 찾기
                    notice_period = dd.text.strip()
                    break  # 찾으면 반복 종료

            # 🔹 딕셔너리 형태로 저장
            job_links.append({
                "notice_url": notice_url,
                "title": notice_title,
                "period": notice_period
            })

        return job_links

    def crawl(self):
        """ 카카오 채용 공고 리스트 크롤링 """
        url = f"{self.base_url}/jobs?skillSet=&part=TECHNOLOGY&company=ALL&keyword=&employeeType=3&page=1"
        html = self.get_html_selenium(url)  # Selenium으로 동적 렌더링된 HTML 가져오기
        if not html:
            return []  # 공고가 없으면 빈 리스트 반환
        return self.parse(html)
