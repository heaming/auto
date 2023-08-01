import asyncio
import time
import sys
import io
from resources.sessionInfo import headers
import schedule
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet
import pytz
import datetime
import tenacity
import aiohttp

BASE_URL = "https://www.thelec.kr/news/articleList.html?view_type=sm"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def thelecRun(msgQue):
    global startTime
    startTime = time.time()
    print("thelecRun()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        await job()
        # print("thelecRun %s" %len(newsSet))
        # print(textList)
        # print(msgQue)
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
            # print("------[thelec] %s ------" %(time.time() - startTime))

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(BASE_URL) as res:
                    if res.status == 200:
                        resText = await res.text()
                        soup = BeautifulSoup(resText, 'html.parser')
                        articles = soup.select(".list-block")

                        for article in articles:
                            if article == recentSubject:
                                break
                            else:
                                recentSubject = article

                            contents = list(article.stripped_strings)
                            writtenAt = contents[len(contents)-1]

                            if(datetime.datetime.strptime(writtenAt, "| %Y-%m-%d %H:%M").hour < now.hour):
                                break
                            if(datetime.datetime.strptime(writtenAt, "| %Y-%m-%d %H:%M").hour == now.hour & datetime.datetime.strptime(writtenAt, "| %Y-%m-%d %H:%M") < datetime.datetime.now() - datetime.timedelta(minutes=1)):
                                break
                                print(writtenAt)

                            title = contents[0]
                            href = "https://www.thelec.kr"+article.select_one('a')['href']
                            # print(title+" "+href)

                            if(isKeyword(title)) and (not isDup(href)):
                                newsSet.add(href)
                                curTxt = title+"\n"+href
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
#     asyncio.run(thelecRun())
#     loop.run_until_complete(thelecRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()
