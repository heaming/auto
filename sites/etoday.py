import asyncio
import time
import sys
import io

import schedule
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet, msgQue
import pytz
import re
import certifi
import datetime
import tenacity


BASE_URL = "https://www.etoday.co.kr/news/flashnews/flash_list"
recentSubject = ""

async def etodayRun():
    global startTime
    startTime = time.time()
    print("etodayRun()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        await job()
        # print("etodayRun :: %s" % len(newsSet))
        # print(text)
        # print("===================")

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

    @tenacity.retry(
        wait=tenacity.wait_fixed(3), # wait 파라미터 추가
        stop=tenacity.stop_after_attempt(100),
    )
    async def job():
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
                    articles = soup.select(".flash_tab_lst > ul > li")

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        contents = list(article.stripped_strings)
                        title = contents[0]
                        writtenAt = contents[1]

                        if(datetime.datetime.strptime(writtenAt, "%H:%M").hour < now.hour):
                            break
                        if(datetime.datetime.strptime(writtenAt, "%H:%M").hour == now.hour & datetime.datetime.strptime(writtenAt, "%H:%M").minute < now.minute):
                            break

                        href = "https://www.etoday.co.kr/news/view/"+re.sub(r'[^0-9]', '', article.select_one('a')['href'])
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href
                            msgQue.append(curTxt)

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
            print("Exception:", str(e))
            asyncio.sleep(3)
            await main()

    await main()

# def mainHandler():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     loop = asyncio.get_event_loop()
#     asyncio.run(etodayRun())
#     loop.run_until_complete(etodayRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()

