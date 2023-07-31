import asyncio
import schedule
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet
import pytz
import datetime
import tenacity


BASE_URL = "https://www.theguru.co.kr/news/article_list_all.html"
recentSubject = ""

@tenacity.retry(
    wait=tenacity.wait_fixed(3), # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def theguruRun(msgQue):
    global startTime
    startTime = time.time()
    print("theguruRun()")

    async def main():
        if(len(newsSet) > 1000):
            newsSet.clear()
        await job()

        # textList = await job()
        print("theguruRun %s" %len(newsSet))
        # print(textList)
        # msgQue.append(textList)
        print(msgQue)
        print("===================")



        # return text
        # bot = telegram.Bot(token=token)
        # await bot.send_message(chat_id, text)

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
            print("------[theguru] %s ------" %(time.time() - startTime))
            curList = []

            with requests.Session() as s:
                res = s.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})

                if res.status_code == requests.codes.ok:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    articles = soup.select(".art_list_all > li")

                    for article in articles:
                        if article == recentSubject:
                            break
                        else:
                            recentSubject = article

                        contents = list(article.stripped_strings)
                        writtenAt = contents[len(contents)-1]

                        if(datetime.datetime.strptime(writtenAt, "%H:%M:%S").hour < now.hour):
                            # print(writtenAt)
                            break
                        if (datetime.datetime.strptime(writtenAt, "%H:%M:%S").hour == now.hour & datetime.datetime.strptime(writtenAt, "%H:%M:%S").minute < now.minute):
                            # print(writtenAt)
                            break

                        # print(contents)
                        title = contents[0]
                        href = "https://www.theguru.co.kr"+article.select_one('a')['href']
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href
                            # curList.append(curTxt)
                            msgQue.put(curTxt)
                            # msgQue.append(curTxt)

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

# def mainHandler():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     loop = asyncio.get_event_loop()
#     asyncio.run(theguruRun())
#     loop.run_until_complete(theguruRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()

