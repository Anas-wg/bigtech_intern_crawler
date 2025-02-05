import os
from flask import Flask, jsonify, render_template,send_from_directory
from collections import defaultdict
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from db.db import collection  # MongoDB 컬렉션 가져오기
from crawlers.naver_crawler import NaverCrawler
from crawlers.kakao_crawler import KakaoCrawler
from crawlers.line_crawler import LineCrawler
from crawlers.woowa_crawler import WoowaCrawler
from crawlers.daangn_crawler import DaangnCrawler
from crawlers.toss_crawler import TossCrawler
from insert_to_mongo import insert_to_mongo
from dotenv import load_dotenv
load_dotenv()

IP = os.environ.get('AWSIP')

DB_PW = os.environ.get("DB_PW")

app = Flask(__name__, static_folder="/home/ubuntu/intern_crawler/intern_zip/static")
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("/home/ubuntu/intern_crawler/intern_zip/static", filename)

# 🔥 MongoDB 설정
# client = MongoClient('localhost', 27017) #27017번 포트
client = MongoClient("mongodb://admin:{DB_PW}@{IP}", 27017)
db = client["job_scraper"]
meta_collection = db["meta"]  # ✅ 같은 job_scraper DB 안에서 meta 컬렉션 사용

# 기본 회사 리스트 (공고가 없어도 0으로 표시되도록 설정)
COMPANIES = ["Naver", "Kakao", "LINE", "Woowa", "Daangn", "Toss"]

def update_last_crawl_time():
    """ 크롤링 시간을 업데이트하는 함수 """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_collection.update_one({"type": "last_crawl"}, {"$set": {"timestamp": now}}, upsert=True)

def scheduled_crawl():
    """ 매일 아침 8시에 실행될 크롤링 작업 """
    print(f"🔍 [스케줄링] 크롤링 시작: {datetime.now()}")

    # 기존 DB 데이터 삭제
    collection.delete_many({})
    print("🗑️ 기존 데이터 삭제 완료!")

    # 크롤링 실행 및 DB 저장
    total_jobs = []
    for Crawler, name in [
        (NaverCrawler, "Naver"),
        (KakaoCrawler, "Kakao"),
        (LineCrawler, "LINE"),
        (WoowaCrawler, "Woowa"),
        (DaangnCrawler, "Daangn"),
        (TossCrawler, "Toss")
    ]:
        print(f"🚀 {name} 크롤링 중...")
        crawler = Crawler()
        jobs = crawler.crawl()
        insert_to_mongo(name, jobs)
        total_jobs.extend(jobs)

    # 크롤링 완료 후 마지막 실행 시간 저장
    update_last_crawl_time()
    print(f"\n✅ 모든 공고 크롤링 & 저장 완료! ({len(total_jobs)}개)")

# 🔥 스케줄러 실행 (Flask 실행 중에도 백그라운드에서 자동 크롤링)
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_crawl, "cron", hour=8, minute=0)  # 매일 오전 8시 실행
scheduler.start()

@app.route("/")
def home():
    """ 기본 웹페이지 렌더링 """
    return render_template("index.html")

@app.route("/api/jobs/count", methods=["GET"])
def get_job_counts():
    """ 회사별 채용 공고 개수 반환 (없으면 0) """
    pipeline = [
        {"$group": {"_id": "$company", "count": {"$sum": 1}}}
    ]
    counts = list(collection.aggregate(pipeline))

    # defaultdict을 사용하여 기본값 0으로 설정
    result = defaultdict(int, {entry["_id"]: entry["count"] for entry in counts})

    return jsonify({company: result[company] for company in COMPANIES})

@app.route("/api/last-crawl", methods=["GET"])
def get_last_crawl_time():
    """ 마지막 크롤링 시간을 반환하는 API """
    last_crawl = meta_collection.find_one({"type": "last_crawl"})
    return jsonify({"last_crawl": last_crawl["timestamp"] if last_crawl else "기록 없음"})

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """ 모든 채용 공고 데이터를 JSON 형태로 반환 (크롤링 없이 기존 데이터만 조회) """
    jobs = list(collection.find({}, {"_id": 0}))
    return jsonify(jobs)

@app.route("/api/jobs/<company>", methods=["GET"])
def get_jobs_by_company(company):
    """ 특정 회사의 채용 공고 데이터를 JSON 형태로 반환 """
    jobs = list(collection.find({"company": company}, {"_id": 0}))
    return jsonify(jobs)

@app.route("/api/crawl", methods=["GET"])
def crawl_jobs():
    """ 사용자가 요청하면 크롤링 실행 후 MongoDB 업데이트 """
    print("🔍 [사용자 요청] 크롤링 시작...")

    # 기존 DB 데이터 삭제
    collection.delete_many({})
    print("🗑️ 기존 데이터 삭제 완료!")

    # 크롤링 실행 및 DB 저장
    total_jobs = []
    for Crawler, name in [
        (NaverCrawler, "Naver"),
        (KakaoCrawler, "Kakao"),
        (LineCrawler, "LINE"),
        (WoowaCrawler, "Woowa"),
        (DaangnCrawler, "Daangn"),
        (TossCrawler, "Toss")
    ]:
        print(f"🚀 {name} 크롤링 중...")
        crawler = Crawler()
        jobs = crawler.crawl()
        insert_to_mongo(name, jobs)
        total_jobs.extend(jobs)

    # 크롤링 후 개수 정보도 업데이트
    update_last_crawl_time()
    job_counts = get_job_counts().json

    print("\n✅ 모든 공고 크롤링 & 저장 완료!")

    return jsonify({"status": "success", "total_jobs": len(total_jobs), "job_counts": job_counts})

if __name__ == "__main__":
    app.run('0.0.0.0', debug=False, port=5000)
