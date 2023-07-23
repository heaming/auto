import time
class SiteInfo:
    def __init__(self, siteName, isDynamic, baseUrl, contentLoc, titleLoc, articleLoc, timeLoc, encodingLang):
        self._siteName = siteName
        self._isDynamic = isDynamic # if it's true, you should use chrome driver
        self._baseUrl = baseUrl # get html from this link
        self._contentLoc = contentLoc
        self._titleLoc = titleLoc # css loc of the title
        self._articleLoc = articleLoc # css loc of the article
        self._timeLoc = timeLoc
        self._encodingLang = encodingLang
        self._startTime = time.time()

    def __str__(self):
        return f"---------[{self._siteName}]----------"

    @property
    def siteName(self):
        return self._siteName

    @siteName.setter
    def siteName(self, siteName):
        self._siteName = siteName


# 그니까 중요한 중복로직이
# session 쓰든 드라이브쓰든
# > url 넣고
# > 기사랑 href 있는 css 파라미터로 넣고
# > 거기서 받아온 문자열리스트에서 기사가 어딨는지 찾고(.li[0] / .div[2] 등등 글구 .li[1]+.li[3] 이렇게 가져오는것두 있음
# > 기사제목 찾고
# > 시간 확인하고
#  > 기사 url 만들어서 붙여주고 (이것도 사이트마다 href 어디서 받아와야 되는지 다르고)
# > 인코딩 해줘야되는 거 utf8 쓰는거 있고 iso어쩌구 쓰는거 있고