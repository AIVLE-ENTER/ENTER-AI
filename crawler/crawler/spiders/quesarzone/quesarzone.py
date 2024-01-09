import rootutils
root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=False)

import pyrootutils
project_root = pyrootutils.setup_root(search_from = __file__,
                                      indicator   = "README.md",
                                      pythonpath  = True)

import re
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

import scrapy
import requests
from bs4 import BeautifulSoup
from w3lib.html import remove_tags
from scrapy_splash import SplashRequest
from utils import Xpath, CrawlerSettings



# 스파이더의 작업 디렉토리를 설정
dir_spiders = Path(__file__).parent.absolute()

# 페이지 수를 계산하는 함수
def page_cnt(keyword):
    url = f"https://quasarzone.com/groupSearches?keyword={keyword}&page=1"
    response = requests.get(url)
    dom=BeautifulSoup(response.text,"html.parser")
    n = int(dom.select("small")[0].text.split()[1].replace(',',''))
    i = n//21+1
    while True:
        url = f"https://quasarzone.com/groupSearches?keyword={keyword}&page={i}"
        response = requests.get(url)
        dom=BeautifulSoup(response.text,"html.parser")
        if not dom.select(".next"):
            return int(i)
            break
        else:
            i = dom.select(".next")[0]['href'].split('=')[2]


# 스파이더 클래스를 정의
class QuesarzoneSpider(scrapy.Spider):
    name = "QuesarzoneSpider"
    custom_settings = CrawlerSettings.get("SPLASH_LOCAL")


    # 초기화 함수를 정의합니다.
    def __init__(self, user_id:str, keyword:str):

        super().__init__()
        self.site     = '퀘이사존'
        self.keyword  = keyword
        self.start_urls      = [f"https://quasarzone.com/groupSearches?keyword={self.keyword}"]
        self.num_page = page_cnt(keyword)
        self.data     = pd.DataFrame(columns=[
                                             'url',
                                             'site',
                                             'document',
                                             'documenttype',
                                             'postdate',
                                             'likes',
                                             'dislike',
                                             'comment_cnt',
                                             'views',
                                             'boardcategory',
                                             'documentcategory'
                                             ])
        self.base_dir = project_root / 'project' / 'user_data' / user_id / 'crawl_data' / keyword /datetime.today().strftime('%Y-%m-%dT%H:%M:%S')



    # Splash Lua 스크립트를 읽어옴
    lua_source = (
        dir_spiders / "quesarzone_main.lua"
    ).open("r", encoding='UTF-8').read()

    # 시작 요청을 생성하는 함수를 정의
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args={"lua_source": self.lua_source},
            )

    # 메인 페이지를 파싱하는 함수를 정의
    def parse(self, response):
        for i in range(1, page_cnt(self.keyword)+1):
            url = f'https://quasarzone.com/groupSearches?keyword={self.keyword}&page={i}'

            # print("parse : ", url)

            yield SplashRequest(
                url=url,
                endpoint="execute",
                args={"lua_source": self.lua_source},
                meta={'url': url},
                callback=self.parse_content,
        )


    # 컨텐츠 페이지를 파싱하는 함수를 정의
    def parse_content(self, response):

        for href in response.xpath('//p[@class="title"]/a/@href'):
            detail_url = href.get()
            post_url = response.urljoin(detail_url)
            # print("parse_content : ", post_url)


            yield SplashRequest(
                url=post_url,
                callback=self.parse_text,
                endpoint="execute",
                args=dict(lua_source=self.lua_source),
            )

    # 텍스트를 파싱하는 함수를 정의
    def parse_text(self, response):

    # 게시글 가져오기
        contents_text = response.xpath("//*[@id='org_contents']//text()").get()
        document  = remove_tags(contents_text)
        # print(document)


    # 날짜 가져오기
        date = response.xpath('//p[@class="right"]/span/text()').get()
        if not date:
            date = response.xpath('//span[@class="date notranslate"]/em/text()').get()
        #print(date)


    # 댓글 수
        comment_cnt = response.xpath('//em[@class="reply"]//text()').get()
        # print(comment_cnt)

    # 댓글
        # comment = response.xpath('//div[@class="reply-con-area"]/div[@class="mid-text-area"]').get()
        # print(comment)

    # 조회수 가져오기
        views = response.xpath('//em[@class="view"]//text()').get()
        # print(views)

    #  게시판 카테고리
        boardcategorys_text = response.xpath('//div[@class="l-title"]//h2//text()').getall()[0]
        boardcategory = re.sub(r'^\d+\s*|\s{2,}', ' ', boardcategorys_text).strip().split('-')[0]
        # print(boardcategory)


        Quesarzone_data = dict(url              = self.start_urls[0],
                               site             = self.site,
                               document         = document,
                               documenttype     = np.NaN, # documenttype 정의해야함 -> 크롤링으로 가져오는게 아니라 fix
                               postdate         = date,
                               likes            = np.NaN,
                               dislike          = np.NaN,
                               comment_cnt      = comment_cnt,
                               views            = views,
                               boardcategory    = boardcategory,
                               documentcategory = np.NaN
                               )

        yield Quesarzone_data

        # df = pd.DataFrame([Quesarzone_data])
        # df.to_csv('quesarzone_data.csv', index=False, mode='a', header=not Path('quesarzone_data.csv').exists())
        # df.to_csv(self.base_dir / f"{self.site}_crawl_data.csv", index=False, mode='a', header=not Path('Quesarzone_data.csv').exists())

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(QuesarzoneSpider, keyword='기가지니', user_id='asdf1234')
    process.start()

# scrapy crawl quesarzone -a keyword='지니뮤직' -o quesarzone.csv
#터미널에 명령어를 입력해야 됨




