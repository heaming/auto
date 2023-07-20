import asyncio
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet, msgQue
import pytz
import datetime

BASE_URL = "https://moneys.mt.co.kr/news/mwList.php?code=w0000&code2=w0100"
recentSubject = ""

async def moneysRun():
    global startTime
    startTime = time.time()
    print("moneysRun()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        await job()
        # print("thelecRun %s" %len(newsSet))
        # print(textList)
        # print(msgQue)
        # print("===================")

    def isKeyword(title):
        if len(list(filter(lambda f: f in title, newsFilter))) > 0:
            return True
        return False

    def isDup(href):
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
            print("------[moneys] %s ------" %(time.time() - startTime))
            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    articles = soup.select('#content > div > ul > .bundle')

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        title = list(article.stripped_strings)[0]
                        href = article.select_one('a')['href']

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href+"\n"+list(article.stripped_strings)[1]
                            msgQue.append(curTxt)

                    # return curList

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

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# loop = asyncio.get_event_loop()
# asyncio.run(moneysRun())
# loop.run_until_complete(moneysRun())
# loop.time()
# loop.close()
