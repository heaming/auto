import asyncio
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet, msgQue
import pytz
import datetime

BASE_URL = "https://www.fnnews.com/newsflash/"
recentSubject = ""

async def fnnewsRun():
    global startTime
    startTime = time.time()
    print("fnnewsRun()")
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

    async def job():
        global recentSubject
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        # if now.hour >= 24 or now.hour <= 6:
        #     return

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

        try:
            print("------[fnnews] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')

                    articles = soup.select(".contents > .wrap_cont > .inner_flash > .list_news > li")
                    # print(articles)

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        title = list(article.stripped_strings)[1]
                        href = "https://www.fnnews.com"+article.select_one('a')['href']
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
#
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# loop = asyncio.get_event_loop()
# asyncio.run(fnnewsRun())
# loop.run_until_complete(fnnewsRun())
# loop.time()
# loop.close()