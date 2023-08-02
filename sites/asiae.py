import asyncio
import time
import sys
import io
from bs4 import BeautifulSoup
from resources.filterList import newsFilter, newsSet
import pytz
import datetime
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tenacity
import schedule

BASE_URL = "https://www.asiae.co.kr/realtime/"
recentSubject = ""


@tenacity.retry(
    wait=tenacity.wait_fixed(3),  # wait 파라미터 추가
    stop=tenacity.stop_after_attempt(100),
)
async def asiaeRun(msgQue):
    print("asiaeRun()")

    async def main():
        if (len(newsSet) > 1000):
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
        wait=tenacity.wait_fixed(3),  # wait 파라미터 추가
        stop=tenacity.stop_after_attempt(100),
    )
    async def job():
        global recentSubject, driver, openedWindow
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))

        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
        options = Options()
        prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2,
                                                            'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                            'notifications': 2, 'auto_select_certificate': 2,
                                                            'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2,
                                                            'media_stream': 2,
                                                            'media_stream_mic': 2, 'media_stream_camera': 2,
                                                            'protocol_handlers': 2,
                                                            'ppapi_broker': 2, 'automatic_downloads': 2,
                                                            'midi_sysex': 2,
                                                            'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                            'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2,
                                                            'site_engagement': 2,
                                                            'durable_storage': 2}}
        options.add_experimental_option('prefs', prefs)
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--headless')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("lang=ko_KR")  # 한국어!

        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(1)
            driver.get(BASE_URL)

            openedWindow = driver.window_handles

            res = driver.page_source
            soup = BeautifulSoup(res, 'html.parser')

            if (len(openedWindow) > 0):
                for win in openedWindow:
                    driver.switch_to.window(win)
                    driver.close()

            articles = soup.select("#pageList > ul > li")

            for article in articles:
                if article == recentSubject:
                    break
                else:
                    recentSubject = article

                writtenAt = list(article.stripped_strings)[0]
                title = list(article.stripped_strings)[1]

                """
                [get time] 
                :: time data not match format error occurs when the date changes
                """
                if (writtenAt.find(':') < 0):
                    return
                if (datetime.datetime.strptime(writtenAt, "%H:%M").hour < now.hour
                        or (datetime.datetime.strptime(writtenAt,
                                                       "%H:%M").hour == now.hour and datetime.datetime.strptime(
                            writtenAt, "%H:%M").minute < (now - datetime.timedelta(minutes=1)).minute)):
                    break

                if (len(list(article.stripped_strings)) > 2):
                    title += list(article.stripped_strings)[2]

                href = "https://www.asiae.co.kr/realtime/sokbo_viewNew.htm?idxno=" + article['id']

                if (isKeyword(title)) and (not isDup(href)):
                    newsSet.add(href)
                    curTxt = title + "\n" + href
                    msgQue.put(curTxt)

        except Exception as e:
            print(str(e))
            for win in openedWindow:
                driver.switch_to.window(win)
                driver.close()
            print("ConnectionError occurred:", str(e))
            print("Retrying in 3 seconds...")

            driver.quit()
            asyncio.sleep(3)
            await main()

    await main()

# def mainHandler():
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     loop = asyncio.get_event_loop()
#     asyncio.run(asiaeRun())
#     loop.run_until_complete(asiaeRun())
#     loop.time()
#
# schedule.every(1).seconds.do(mainHandler)
#
# while True:
#     schedule.run_pending()
