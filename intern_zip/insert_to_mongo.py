from db.db import collection

def insert_to_mongo(company_name, jobs):
    """ MongoDB에 크롤링한 채용 공고 저장 """
    if not jobs:
        print(f"🚫 {company_name} 공고가 없습니다. (기존 데이터 유지)")
        return  # 기존 데이터를 유지하기 위해 삭제하지 않음

    # 기존 동일한 회사 공고 삭제 후 저장 (업데이트를 위함)
    collection.delete_many({"company": company_name})

    for job in jobs:
        job_data = {
            "company": company_name,  # 회사 이름 추가
            "title": job["title"],
            "notice_url": job["notice_url"],
            "period": job["period"]
        }
        collection.insert_one(job_data)  # MongoDB에 저장

    print(f"✅ {company_name} 공고 {len(jobs)}개 저장 완료!")
