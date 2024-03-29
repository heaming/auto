# -*- coding: utf-8 -*-
import re

import requests
import telegram
import asyncio
import schedule
import time
import sys
import io
from bs4 import BeautifulSoup
import pytz
import datetime
import tenacity
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from resources.filterList import newsFilter, newsSet


BASE_URL = "https://www.news1.kr/latest/"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def news1Run(msgQue):
    print("news1Run()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        await job()

    def isKeyword(title):
        # print(title)
        if len(list(filter(lambda f: f in title, newsFilter))) > 0:
            return True
        return False

    def isDup(href):
        if href in newsSet:
            return True
        return False

    @tenacity.retry(
        wait=tenacity.wait_fixed(3), # wait 파라미터 추가
        stop=tenacity.stop_after_attempt(100),
    )
    async def job():
        global recentSubject, driver, openedWindow
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

        options = Options()
        options.add_argument('--headless')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("lang=ko_KR") # 한국어!

        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(1)
            driver.get(BASE_URL)

            openedWindow = driver.window_handles

            res = driver.page_source
            soup = BeautifulSoup(res, 'html.parser')

            if(len(openedWindow) > 0):
                for win in openedWindow:
                    driver.switch_to.window(win)
                    driver.close()

            articles = soup.select(".article_list > .article")

            for article in articles:
                if article == recentSubject:
                    break
                else:
                    recentSubject = article

                contents = list(article.stripped_strings)
                writtenAt = contents[len(contents)-2]

                if(not '초전' in writtenAt and not '1분전' in writtenAt):
                    print("없음")
                    break
                    
                title = contents[0]

                href = "https://www.news1.kr"+article.select_one('a')['href']

                if(isKeyword(title)) and (not isDup(href)):
                    newsSet.add(href)
                    curTxt = title+"\n"+href
                    msgQue.put(curTxt)

        except requests.exceptions.ConnectionError as e:
            print("ConnectionError occurred:", str(e))
            print("Retrying in 3 seconds...")
            asyncio.sleep(3)
            await main()

        except asyncio.futures.TimeoutError as e:
            print("asyncio TimeoutError:", str(e))
            asyncio.sleep(3)
            await main()

        except Exception as e:
            for win in openedWindow:
                driver.switch_to.window(win)
                driver.close()
            print("ConnectionError occurred:", str(e))
            print("Retrying in 3 seconds...")

            driver.quit()
            asyncio.sleep(3)
            await main()

        driver.quit()
    await main()

# def mainHandler():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     loop = asyncio.get_event_loop()
#     asyncio.run(news1Run())
#     loop.run_until_complete(news1Run())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()
