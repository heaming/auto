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
from resources.telegramInfo import token, chat_id

newsFilter = filterList.newsFilter
BASE_URL = "http://www.thebell.co.kr/free/content/Article.asp?svccode=00"
recentSubject = ""
newsSet = set()

def thebellRun():
    global startTime
    startTime = time.time()
    print("thebellRun()")
    async def main(text):
        if(len(newsSet) > 1000):
            newsSet.clear()
        print("thebellRun %s" %len(newsSet))
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
            print("------[thebell] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')

                    articles = soup.select(".newsList > .listBox > ul > li > dl")

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        contents = list(article.stripped_strings)
                        title = ""
                        content = ""

                        if(len(contents) > 1):
                            content += "\n"+list(article.stripped_strings)[1]

                        title += contents[0]
                        href = "http://www.thebell.co.kr/free/content/"+article.select_one('a')['href']
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href+content
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

# thebellRun()
