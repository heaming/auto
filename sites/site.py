class SiteInfo:
    def __init__(self, siteName, url, cssTag, newsLink, iframe):
        self.siteName = siteName
        self.url = url
        self.cssTag = cssTag
        self.newsLink = newsLink
        self.iframe = iframe

siteInfos = [
    SiteInfo("머니S", "https://moneys.mt.co.kr/news/mwList.php?code=w0000&code2=w0100", "#content > div > ul > .bundle", ""),
    SiteInfo("이투데이", "https://www.etoday.co.kr/news/flashnews/", "ul > li > .flash_tab_txt t_reduce", "https://www.etoday.co.kr/news/flashnews/flash_view?idxno="),
    # SiteInfo("아시아경제", "https://www.asiae.co.kr/realtime/", "", ""),
    SiteInfo("더구루", "https://www.theguru.co.kr/news/article_list_all.html", ".art_list_all > li", "https://www.theguru.co.kr"),
    SiteInfo("디알렉", "https://www.thelec.kr/news/articleList.html?view_type=sm", "list-block", "https://www.thelec.kr")
]

# https://www.etoday.co.kr/news/section/subsection?MID=1202 <--오른쪽 상단 속보창  -- 이투데이
# 머니S
# https://www.asiae.co.kr/realtime/ --아시아경제
# https://www.theguru.co.kr/news/article_list_all.html -- 더구루https://www.thelec.kr/news/articleList.html?view_type=sm --디알렉