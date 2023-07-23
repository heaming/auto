import pytz
import datetime
import sys
import io
import requests
from bs4 import BeautifulSoup

async def job(BASE_URL):
    global recentSubject
    now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    # if now.hour >= 24 or now.hour <= 6:
    #     return

    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

    with requests.Session() as s:
        res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        # res.raise_for_status()
        # res.encoding = None #ISO-8859-1 처리

        if res.status_code == requests.codes.ok:
            # print(res.encoding)
            soup = BeautifulSoup(res.text, 'html.parser')

            articles = soup.select(".article > .articleList2 > li > div > .txtCont")

            for article in articles:
                if article == recentSubject:
                    break
                else:
                    recentSubject = article

                title = list(article.stripped_strings)[0]