import asyncio
import time
import sys
import io

import schedule
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet
import pytz
import datetime
import tenacity

BASE_URL = "https://www.yna.co.kr/news?site=footer_news_latest"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def ynaRun(msgQue):
    global startTime
    startTime = time.time()
    print("ynaRun()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        print(msgQue)
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
            print("------[yna] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')

                    articles = soup.select(".list > li > div > .news-con")
                    times = soup.select(".list > li > div > div > .txt-time")

                    for i in range(len(articles)):

                        article = articles[i]
                        # print(article)
                        writtenAt = list(times[i].stripped_strings)[0]

                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        if(datetime.datetime.strptime(writtenAt, "%m-%d %H:%M").hour < now.hour):
                            # print(writtenAt)
                            break
                        if (datetime.datetime.strptime(writtenAt, "%m-%d %H:%M").hour == now.hour & datetime.datetime.strptime(writtenAt, "%m-%d %H:%M").minute-2 < now.minute):
                            # print(writtenAt)
                            break

                        contents = list(article.stripped_strings)
                        title = ""
                        content = ""

                        if(len(contents) > 1):
                            content += "\n"+list(article.stripped_strings)[1]

                        title += contents[0]
                        href = "https://"+article.select_one('a')['href'].replace("//", "")
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href+content
                            msgQue.put(curTxt)
                            # msgQue.append(curTxt)


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
#     asyncio.run(ynaRun())
#     loop.run_until_complete(ynaRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()
