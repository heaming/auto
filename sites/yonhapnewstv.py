import asyncio
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet, msgQue
import pytz
import datetime
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tenacity

BASE_URL = "https://www.yonhapnewstv.co.kr/news?ct=1"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def yonhapnewstvRun():
    global startTime
    startTime = time.time()
    print("yonhapnewstvRun()")

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
        # print(href)
        if href in newsSet:
            return True
        return False

    async def job():
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

            if(len(openedWindow) > 0):
                for win in openedWindow:
                    driver.switch_to.window(win)
                    driver.close()

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
                    msgQue.append(curTxt)

            driver.quit()

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

    await main()

# yonhapnewstvRun()
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# loop = asyncio.get_event_loop()
# asyncio.run(yonhapnewstvRun())
# loop.run_until_complete(yonhapnewstvRun())
# loop.time()
# loop.close()