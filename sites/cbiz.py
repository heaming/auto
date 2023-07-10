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
import logging
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import re

newsFilter = filterList.newsFilter
BASE_URL = "https://cbiz.chosun.com/svc/bulletin/index.html"
recentSubject = ""
# token = "1851203279:AAES64ZdTQz8Eld-zuuT-j3Sg3hOskVvAl4"
token = "6370344836:AAFXDbpiuR1vbbkwDdJFYBdFds4q3C7CXF0"
bot = telegram.Bot(token=token)
# chat_id = '-1001524509726'  # 채널
chat_id = '5915719482'
newsSet = set()

def cbizRun():
    global startTime
    startTime = time.time()
    print("cbizRun()")
    async def main(text):
        if(len(newsSet) > 1000):
            newsSet.clear()
        print("cbizRun %s" %len(newsSet))
        print(text)
        print("===================")
        # token = "1851203279:AAES64ZdTQz8Eld-zuuT-j3Sg3hOskVvAl4"
        # bot = telegram.Bot(token=token)
        # await bot.send_message(chat_id, text)

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
            print("------[cbiz] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
                res.raise_for_status()
                res.encoding = None #ISO-8859-1 처리

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')

                    articles = soup.select(".article_list > ul > li")

                    for article in articles:
                        # print(article)
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        contents = list(article.stripped_strings)
                        # title = ""
                        # content = ""
                        #
                        # if(len(contents) > 1):
                        #     content += "\n"+list(article.stripped_strings)[1]

                        title = contents[0]
                        href = "https://cbiz.chosun.com"+article.select_one('a')['href']
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

cbizRun()