import requests
import telegram
import asyncio
import schedule
import time
import sys
import io
from bs4 import BeautifulSoup
import requests
from filterList import *
import pytz
import datetime
import logging
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
from moneys import moneysRun
from etoday import etodayRun
from thelec import thelecRun
from theguru import theguruRun

recentSubject = ""
token = "1851203279:AAES64ZdTQz8Eld-zuuT-j3Sg3hOskVvAl4"
# bot = telegram.Bot(token=token)
chat_id = '-1001524509726'  # 채널

if __name__ == "__main__":
    pMoneyS = Process(target=moneysRun)
    pEtoday = Process(target=etodayRun)
    pThelec = Process(target=thelecRun)
    pTheguru = Process(target=theguruRun)


    while True:
        pMoneyS.start(); pMoneyS.join()
        pEtoday.start(); pEtoday.join()
        pThelec.start(); pThelec.join()
        pTheguru.start(); pTheguru.join()





# 1.파이썬 언어
# 2.스케줄링 (구현되어있음) - vscode로 기동해놓으면 앱종료하지 않는이상 계속 뉴스 긁어와야함
# 3.여러 뉴스 사이트에서 '동시에' 뉴스 가져와야함 (사이트목록은 추후 드림. 일단은 머니S, 아시아경제,이데일리 최신뉴스 가져오는걸로 )
# 4.키워드가 포함되어 있는 뉴스를 가져와야함 (구현되어있음)
# 5.뉴스를 현재 하나씩 가져오는데 tobe에서는 3개or 5개씩 가져와서 이미 보낸뉴스는 제외하고 텔레그램으로 전송해야함
# 6.리스트에 쌓는다면 리스트 천건 이상 되면 지우도록 (성능 때문에 and vscode 며칠씩 켜놓는 경우 많은데 리스트 쌓이면 느릴까봐? )
# 7.뉴스 스크래핑할때 사이트마다 봇인줄알고 연결 끊어버리는 경우가 있던데 끊으면 재연결 되어야함 (현재 구현되

# [박영일] [오전 8:57] Ide는 상관 없어요
# 네 상단 기사만 가져오는거 맞아요
# 기사가 1초에 여러개뜨게되면
# 카톡 , 임상 , 속보 , 토마토는 못가져와요
# 저거 5개를 가져와서 키워드에 맞는거만 보내면 돼요
# 임상, 속보, 매각 세개 메시지 보내는 거죠
#
#
# [박영일] [오전 8:58] 한페이지에 제목에해당하는 태그 다긁으면 되는데
# 이게 사이트 20개라 치고 한페이지 15개 기사가 있고
# 초당 300개씩 리스트 쌓이면
# 시간지나면 뭔가.. 성능에 문제있지않을까? 싶어서 하나만 긁어오도록 한거에여
#
# [박영일] [오전 8:59] 네 중복방지용 리스트요!
# [박영일] [오전 9:00] 보낼때 한번에 여러개를 보내면 안받아줄거에요 그래서 리스트에서 쌓아두고 순차적으로 보내는걸 생각했어요
#
# [박영일] [오전 9:02] 제가 너무 설명을 거지같이했네요 ㅎㅎ,,
# [박영일] [오전 9:05] 뉴스를 초당 계속 스크래핑하면 사이트에서 봇인줄알고 끊어버리는? 경우가있어서 그걸 방지해야하구요
#
# 텔레그램도 한번에 보내는게 안될거에요
# 카톡도 피시로 한번에 메세지 여러개 보내는거 방지해놨자나요
# 텔레그램도 저 전송 api 호출하는거 한번에 여러번 못하도록 막아놨을거에요


