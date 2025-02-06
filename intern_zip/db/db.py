from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

IP = os.environ.get('AWSIP')

DB_PW = os.environ.get("DB_PW")

# MongoDB 연결 설정
client = MongoClient(f"mongodb://admin:{DB_PW}@{IP}", 27017)
db = client.job_scraper  # 사용할 DB 이름
collection = db.jobs  # 저장할 Collection (채용 공고)
