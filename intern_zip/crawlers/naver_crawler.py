# crawlers/naver_crawler.py
from bs4 import BeautifulSoup
import re
from .base_crawler import BaseCrawler

class NaverCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://recruit.navercorp.com")

    def parse(self, html):
        """ 네이버 채용 공고를 크롤링하는 함수 """
        soup = BeautifulSoup(html, "html.parser")
        notices = soup.select(".card_wrap > .card_list > li")
        base_url = f"{self.base_url}/rcrt/view.do?annoId="

        job_links = []
        for notice in notices:
            tag_element = notice.select_one("a")
            if tag_element:
                notice_title = tag_element.select_one("h4").text.strip()  # 제목 가져오기
                notice_info = tag_element.select_one("dl")

                notice_period = None  # 모집 기간 기본값 설정
                notice_part = None
                if notice_info:
                    dt_elements = notice_info.select("dt")  # 모든 dt 태그 가져오기
                    dd_elements = notice_info.select("dd")  # 모든 dd 태그 가져오기

                    # dt와 dd가 짝을 이루므로, "모집 기간"을 찾아 해당 dd 값을 가져옴
                    for dt, dd in zip(dt_elements, dd_elements):
                        if dt.text.strip() == "모집 분야":
                            notice_part = dd.text.strip()
                        if dt.text.strip() == "모집 기간":  # "모집 기간"인 dt 찾기
                            notice_period = dd.text.strip()  # 해당하는 dd의 텍스트 가져오기
                            break  # 찾으면 반복 종료
                
                onclick_attr = tag_element.get("onclick")
                notice_url = None  # URL 기본값 설정
                if onclick_attr:
                    match = re.search(r"show\('(\d+)'\)", onclick_attr)
                    if match:
                        notice_number = match.group(1)
                        notice_url = base_url + notice_number

                # 🔹 모집 기간을 포함해 딕셔너리 저장
                job_links.append({
                    "notice_url": notice_url,
                    "title": notice_title,
                    "period": notice_period,  # 모집 기간 추가
                })

        return job_links


    def crawl(self):
        """ 네이버 채용 공고 리스트 크롤링 """
        url = "https://recruit.navercorp.com/rcrt/list.do?subJobCdArr=1010001%2C1010002%2C1010003%2C1010004%2C1010005%2C1010006%2C1010007%2C1010008%2C1010020%2C1020001%2C1030001%2C1030002%2C1040001%2C1050001%2C1050002%2C1060001&sysCompanyCdArr=&empTypeCdArr=0040"
        html = self.get_html(url)
        if html:
            return self.parse(html)
        return []
