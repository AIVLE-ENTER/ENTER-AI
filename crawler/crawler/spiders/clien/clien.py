import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import Request, TextResponse
from scrapy.utils.request import fingerprint
import numpy as np
import pandas as pd
import requests
import re
import rootutils
root = rootutils.setup_root(
    __file__, dotenv=True, pythonpath=True, cwd=False)

from typing import Iterable
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from utils import Xpath, CrawlerSettings
from bs4 import BeautifulSoup
from w3lib.html import remove_tags

# 스파이더의 작업 디렉토리를 설정
dir_spiders = Path(__file__).parent.absolute()


# 스파이더 클래스를 정의
class ClienSpider(scrapy.Spider):
    name = "clien"


    # 초기화 함수를 정의합니다.
    def __init__(self,keyword):
        super().__init__()
        self.site = 'clien'
        self.keyword = keyword
        self.url = [f"https://www.clien.net/service/search?q={self.keyword}"]
        self.data = pd.DataFrame(columns=[
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

    # Splash Lua 스크립트를 읽어옴
    lua_source = (
        dir_spiders / "clien_main.lua"
    ).open("r", encoding='UTF-8').read()

        # 시작 요청을 생성하는 함수를 정의
    def start_requests(self):
        i=0

        while i<1:
            url = f"https://www.clien.net/service/search?q={self.keyword}&sort=recency&p={i}&boardCd=&isBoard=false"
            # print(url)
            response = requests.get(url)
            dom=BeautifulSoup(response.text,"html.parser")
            elements = dom.select(".board-nav-page")
            if not elements:
                break
            content = dom.select(".subject_fixed")
            for j in range(len(content)):
                post_url = "https://www.clien.net"+content[j]['href']
                # print(post_url)
                yield SplashRequest(
                        url=post_url,
                        callback=self.parse,
                        endpoint="execute",
                        args={"lua_source": self.lua_source},
                    )
            i+=1

        # 메인 페이지를 파싱하는 함수를 정의
    def parse(self, response):
        # 제목
        titles = response.xpath('//head/title')[0].get()
        # print(titles)

        # 댓글수
        comment_cnt = response.xpath('//a[@class="post_reply"]/span//text()').get()
        if not comment_cnt:
            comment_cnt = 0
        # print(commentcnt)

        # 게시글 카테고리
        documentcategory = response.xpath('//span[@class="post_category"]//text()').get()
        # print(documentcategory)

        # 게시판 카테고리
        boardcategory = response.xpath('//div[@class="board_name"]//a//text()').get()
        # print(boardcategory)

        # 좋아요
        likes = response.xpath('//a[@class="symph_count"]//text() | //a[@class="symph_count disable"]//text()').get()
        # print(likes)

        # 조회수
        views = response.xpath('//span[@class="view_count"]//strong/text()').get()
        # print(views)

        # 날짜
        postdate = response.xpath('//div[@class="post_author"]/span')[0].get()
        date = remove_tags(postdate)
        def clean_date(date_str):
            cleaned_date = re.sub(r'\s{3,}', ' ', date_str)  # 세칸 이상의 띄어쓰기를 하나로 변환
            cleaned_date = re.sub(r'\s*수정일\s*:\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', date_str)  # "수정일" 이후 제거
            return cleaned_date.strip()

        date = clean_date(date)

        # print(date)

        # 게시글
        document = response.xpath('//div[@class="post_article"]/p/text()').getall()
        # print(document)
        # print()

        clien_data = {'url':                      self.url,
                      'site':                     self.site,
                      'document':                 document,
                      'documenttype':             np.NAN,
                      'postdate':                 date,
                      'likes' :                   likes,
                      'dislike' :                 np.NAN,
                      'comment_cnt' :             comment_cnt,
                      'views':                    views,
                      'boardcategory' :           boardcategory,
                      'documentcategory' :        documentcategory}
        yield clien_data
        # df = pd.DataFrame([clien_data])
        # df.to_csv('clien_data.csv', index=False, mode='a', header=not Path('clien_data.csv').exists())


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(ClienSpider, keyword='지니뮤직')
    process.start()

# scrapy crawl clien -a keyword='지니뮤직' -o clien.csv
# 터미널에 명령어 입력해야함