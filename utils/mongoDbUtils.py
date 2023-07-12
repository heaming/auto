from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

uri = "mongodb+srv://heymi:fnffnfkffk98@cluster0.upa45og.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.new_data

try:
    # [ site_name / title / url / keyword / contents / writer / written_at / created_at ]

    sample = {
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
    # print("You successfully connected to MongoDB!")
except Exception as e:
    print(e)
