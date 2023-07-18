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
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from resources.telegramInfo import token, chat_id, bot

newsFilter = filterList.newsFilter
BASE_URL = "https://www.yonhapnewstv.co.kr/news?ct=1"
recentSubject = ""
newsSet = set()

def yonhapnewstvRun():
    global startTime
    startTime = time.time()
    print("yonhapnewstvRun()")

    async def main(text):
        if(len(newsSet) > 1000):
            newsSet.clear()
        print("yonhapnewstvRun %s" %len(newsSet))
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
        global recentSubject, driver, openedWindow
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        # if now.hour >= 24 or now.hour <= 6:
        #     return

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

        options = Options()
        options.add_argument('--headless')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("lang=ko_KR") # 한국어!

        try:
            print("------[yonhapnewstv] %s ------" % (time.time() - startTime))

            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(1)
            driver.get(BASE_URL)

            openedWindow = driver.window_handles
            res = driver.page_source
            soup = BeautifulSoup(res, 'html.parser')

            articles = soup.select("#content > .inner > .cont-row > div > ul > li > div > .item-body")

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

                title += list(article.stripped_strings)[0]
                href = "https://www.yonhapnewstv.co.kr"+article.select_one('a')['href']
                # print(title+" "+href)

                if(isKeyword(title)) and (not isDup(href)):
                    newsSet.add(href)
                    curTxt = title+"\n"+href+content
                    asyncio.run(main(curTxt))


        except:
            if(len(openedWindow) > 0):
                for win in openedWindow:
                    driver.switch_to.window(win)
                    driver.close()

            print("ConnectionError occurred:")
            print("Retrying in 3 seconds...")

            driver.quit()
            time.sleep(3)
            job()

    schedule.every(1).seconds.do(job)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while True:
        schedule.run_pending()
        time.sleep(1)

# yonhapnewstvRun()
