from pymongo import MongoClient

# MongoDB 연결 설정
client = MongoClient('localhost', 27017)
db = client.job_scraper  # 사용할 DB 이름
collection = db.jobs  # 저장할 Collection (채용 공고)
