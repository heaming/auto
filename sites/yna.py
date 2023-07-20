import asyncio
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from resources.filterList import newsFilter, newsSet, msgQue
import pytz
import datetime

BASE_URL = "https://www.yna.co.kr/news?site=footer_news_latest"
recentSubject = ""

async def ynaRun():
    global startTime
    startTime = time.time()
    print("ynaRun()")

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

                    # print(soup)
                    # frameSoup = soup.select_one('iframe', '#flash_list')
                    # iframeUrl = BASE_URL+frame['src']
                    # resIframe = requests.get(iframeUrl.text, 'html.parser')
                    articles = soup.select(".list > li > div > .news-con")

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

                        title += contents[0]
                        href = "https://"+article.select_one('a')['href'].replace("//", "")
                        # print(title+" "+href)

                        if(isKeyword(title)) and (not isDup(href)):
                            newsSet.add(href)
                            curTxt = title+"\n"+href+content
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

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# loop = asyncio.get_event_loop()
# asyncio.run(ynaRun())
# loop.run_until_complete(ynaRun())
# loop.time()
# loop.close()