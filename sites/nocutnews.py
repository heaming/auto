import asyncio
import time
import sys
import io
import aiohttp
import schedule
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet
import pytz
import datetime
import tenacity
from resources.sessionInfo import headers

BASE_URL = "https://www.nocutnews.co.kr/news/list"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def nocutnewsRun(msgQue):
    print("nocutnewsRun()")
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

    @tenacity.retry(
        wait=tenacity.wait_fixed(3), # wait 파라미터 추가
        stop=tenacity.stop_after_attempt(100),
    )
    async def job():
        global recentSubject
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(BASE_URL) as res:
                    if res.status == 200:
                        resText = await res.text()
                        soup = BeautifulSoup(resText, 'html.parser')
                        articles = soup.select("#pnlNewsList > ul > li > dl")

                        for article in articles:
                            if article == recentSubject:
                                break
                            else:
                                recentSubject = article

                            contents = list(article.stripped_strings)
                            title = ""
                            content = ""

                            temp = contents[len(contents)-1].split(" ")
                            writtenAt = temp[len(temp)-1]

                            if(datetime.datetime.strptime(writtenAt, "%I:%M:%S").hour < now.hour
                                    or (datetime.datetime.strptime(writtenAt, "%I:%M:%S").hour == now.hour and datetime.datetime.strptime(writtenAt, "%I:%M:%S").minute < (now - datetime.timedelta(minutes=1)).minute)):
                                break

                            if(len(contents) > 1):
                                content += "\n"+list(article.stripped_strings)[1]

                            title += contents[0]
                            href = "https://www.nocutnews.co.kr"+article.select_one('a')['href']
                            # print(title+" "+href)

                            if(isKeyword(title)) and (not isDup(href)):
                                newsSet.add(href)
                                curTxt = title+"\n"+href+content
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
            print("Exception:", str(e))
            asyncio.sleep(3)
            await main()

    await main()

# def mainHandler():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     loop = asyncio.get_event_loop()
#     asyncio.run(nocutnewsRun())
#     loop.run_until_complete(nocutnewsRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()
