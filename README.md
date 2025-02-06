## 빅테크 개발자 인턴십 공고 크롤러

개발기간 : 2025.02.02 ~ 2025.02.05

### 배포 주소

## http://intern-crawler.site/

모바일에 최적화 되어 있습니다!

### Tech Stacks

### 주요 기능📦

---

#### ⭐️ 빅테크 기업별 공고 개수 확인

- 네이버, 카카오, 라인, 우아한 형제들(배달의 민족), 당근, 토스 채용 페이지 내 인턴십 공고 크롤링

- 🚨 쿠팡같은 경우 인턴 공고 필터링이 없습니다. 쿼리에 검색어를 집어넣는 방식을 통해 가져올 예정입니다.

#### ⭐️ 전체, 세부 공고 내용 확인

- DropDown을 활용하여 전체 혹은 기업별 공고를 확인할 수 있습니다.

### 아키텍처

<!-- 아키텍쳐 이미지 -->

```
📦intern_zip
 ┣ 📂__pycache__
 ┃ ┣ 📜db.cpython-313.pyc
 ┃ ┗ 📜insert_to_mongo.cpython-313.pyc
 ┣ 📂crawlers
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜base_crawler.py
 ┃ ┣ 📜daangn_crawler.py
 ┃ ┣ 📜kakao_crawler.py
 ┃ ┣ 📜line_crawler.py
 ┃ ┣ 📜naver_crawler.py
 ┃ ┣ 📜toss_crawler.py
 ┃ ┗ 📜woowa_crawler.py
 ┣ 📂db
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┗ 📜db.cpython-313.pyc
 ┃ ┗ 📜db.py
 ┣ 📂static
 ┃ ┗ 📜styles.css
 ┣ 📂templates
 ┃ ┗ 📜index.html
 ┣ 📜app.py
 ┣ 📜insert_to_mongo.py
 ┗ 📜practice.py
```
