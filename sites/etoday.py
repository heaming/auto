import certifi
import trio
import telegram
import trio_asyncio
import ssl
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
import re
from resources.telegramInfo import token, chat_id, bot

newsFilter = filterList.newsFilter
BASE_URL = "https://www.etoday.co.kr/news/flashnews/flash_list"
recentSubject = ""
newsSet = set()

def etodayRun():
    global startTime
    startTime = time.time()
    print("etodayRun()")

    async def main(text):
        if(len(newsSet) > 1000):
            newsSet.clear()
        print("etodayRun :: %s" % len(newsSet))
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
            print("------[etoday] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'}, verify=certifi.where())

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    articles = soup.select(".flash_tab_txt")
                    # print(articles)
                    # articles = resIframe.select("ul > li > .flash_tab_txt t_reduce")

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        title = list(article.stripped_strings)[0]
                        href = "https://www.etoday.co.kr/news/view/"+re.sub(r'[^0-9]', '', article.select_one('a')['href'])
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href
                            asyncio.run(main(curTxt))
                            # trio_asyncio.run(main(curTxt))
        except ssl.SSLWantReadError as e:
            print(e)
            return

        except requests.exceptions.ConnectionError as e:
            print("ConnectionError occurred:", str(e))
            print("Retrying in 3 seconds...")
            time.sleep(3)
            job()

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    schedule.every(1).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

# etodayRun()
