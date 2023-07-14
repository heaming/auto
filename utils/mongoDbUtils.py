from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from resources.mongoInfo import uri

# global stack :: insert datas per 0.5hour
newsDetail = []

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.new_data

try:
    # [ site_name / title / url / keyword / contents / writer / written_at / created_at ]

    sample = {
        'news_id' : 'sample'+datetime.now().timestamp()+len(newsDetail), #site_name+written_at+datetime.now().date+len(newsDetail)
        'site_name': 'sample',
        'title': 'title',
        'url': 'www.naver.com',
        'keyword': '샘풀',
        'contents': '몰라!',
        'writer': 'heymi',
        'written_at': '20230710',
        'created_at': datetime.now()
    }
    db.users.insert_one(sample)

    # client.admin.command('ping')
except Exception as e:
    print(e)
