# -*- coding: utf-8 -*-
import requests
import telegram
import asyncio
import schedule
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources import filterList
import pytz
import datetime
from resources.telegramInfo import token, chat_id, bot

newsFilter = filterList.newsFilter
BASE_URL = "https://www.sedaily.com/News/HeadLine/HeadLineListAjax"
recentSubject = ""
newsSet = set()

def sedailyRun():
    global startTime
    startTime = time.time()
    print("sedailyRun()")
    async def main(text):
        if(len(newsSet) > 1000):
            newsSet.clear()
        print("sedailyRun %s" %len(newsSet))
        print(text)
        print("===================")
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id, text)

    def isKeyword(title):
        # print(title)
        if len(list(filter(lambda f: f in title, newsFilter))) > 0:
            return True
        return False

    def isDup(href):
        # print(href)
        if href in newsSet:
            return True
        return False

    def job():
        global recentSubject
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        # if now.hour >= 24 or now.hour <= 6:
        #     return

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

        try:
            print("------[sedaily] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
                res.raise_for_status()
                res.encoding = None #ISO-8859-1 처리

                if res.status_code == requests.codes.ok:
                    # print(res.encoding)
                    soup = BeautifulSoup(res.text, 'html.parser')

                    # frameSoup = soup.select_one('iframe', '#flash_list')
                    # iframeUrl = BASE_URL+frame['src']
                    # resIframe = requests.get(iframeUrl.text, 'html.parser')
                    articles = soup.select(".headline_list > ul > li")
                    # print(articles)

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        title = list(article.stripped_strings)[0]
                        # print(article.select_one('a')['href'])

                        nId = article.select_one('a')['href'].replace("javascript:NewsView(\'", '').replace("\');", '')

                        href = "https://www.sedaily.com/News/HeadLine/HeadLineViewAjax?Nid="+nId+"&NClass=AL&Keyword=&HeadLineTime=1"
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href
                            asyncio.run(main(curTxt))


        except requests.exceptions.ConnectionError as e:
            print("ConnectionError occurred:", str(e))
            print("Retrying in 3 seconds...")
            time.sleep(3)
            job()

    schedule.every(1).seconds.do(job)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while True:
        schedule.run_pending()
        time.sleep(1)

# sedailyRun()
