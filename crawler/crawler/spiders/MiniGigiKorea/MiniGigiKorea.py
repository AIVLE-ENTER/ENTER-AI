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

class MiniGigiKoreaSpider(scrapy.Spider):
    name = "MiniGigiKorea"
    custom_settings = CrawlerSettings.get("SPLASH_LOCAL")

    # 초기화 함수를 정의합니다.
    def __init__(self,keyword):
        super().__init__()

        self.site = 'MiniGigiKorea'
        self.keyword = keyword
        self.start_urls = [f"https://meeco.kr/?_filter=search&act=&vid=&mid=ITplus&category=&search_target=title_content&search_keyword={self.keyword}"]

    # Splash Lua 스크립트를 읽어옴
    lua_source = (
        dir_spiders / "MiniGigiKorea_main.lua"
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

    def parse(self, response):
        # 확인
        # print(response)
        next_page_url = response.xpath('//div[@class="paging bBt"]/a[@class="pageNext"]/@href').get()
        # print("next_page_url : ",  'https://meeco.kr' + next_page_url)
        if next_page_url:
            yield SplashRequest(
                url=response.urljoin(next_page_url),
                callback=self.parse_page_cnt,
                endpoint="execute",
                args={"lua_source": self.lua_source},
            )

    def parse_page_cnt(self, response):
        last_page_number = int(response.xpath('//div[@class="paging bBt"]/a[@class="pageNum on num"]/text()').get())
        # print(f'Last Page Number: {last_page_number}')
        if last_page_number == 1:
            url = f'https://meeco.kr/?_filter=search&act=&vid=&mid=ITplus&category=&search_target=title_content&search_keyword={self.keyword}'
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse_info)
        else:
            for i in range(1, last_page_number+1):
                url = f'https://meeco.kr/index.php?_filter=search&mid=ITplus&search_target=title_content&search_keyword={self.keyword}&division=-38162354&last_division=-35713619&page={i}'

                yield SplashRequest(
                    url=url,
                    callback=self.parse_info,
                    endpoint="execute",
                    args={"lua_source": self.lua_source},
                )


    def parse_info(self, response):
        # print("response: ", response)
        for href in response.xpath('//td[@class="title"]/a[@class="title_a title_moa"]/@href'):
            detail_url = href.get()
            post_url = response.urljoin(detail_url)
            # print(post_url)
            yield SplashRequest(
                    url=post_url,
                    callback=self.parse_detail,
                    endpoint="execute",
                    args={"lua_source": self.lua_source},
                )

    def parse_detail(self, response):
        # 게시글 가져오기

        # print("response: ", response)

        #1번
        # contents_elements = response.xpath('//div[@class="atc-wrap"]/div[contains(@class, "xe_content")]/p[string-length(normalize-space(.)) > 0]')
        # contents_text = " ".join(contents_elements.xpath('string(.)').getall())
        # print("contents : ", contents_text)

        #2번이 더 잘 나옴
        contents_elements = response.xpath('//*[@id="bBd"]/article/div[1]/div[2]')
        contents_text_list = contents_elements.xpath('string(.)').getall()

        # 각 텍스트를 공백을 제거하고 빈 문자열은 제외합니다.
        contents_text_list = [text.strip() for text in contents_text_list if text.strip()]

        # 정규표현식을 사용하여 공백, 개행 등을 모두 공백 하나로 치환합니다.
        document = re.sub(r'\s+', ' ', ' '.join(contents_text_list))

        # print("contents : ", document)
        # print()

        # 게시 날짜
        date = response.xpath('//*[@id="bBd"]/article/header/ul[1]/li[3]').get()
        postdate = remove_tags(date)
        # print(postdate)

        # 좋아요
        like = response.xpath('//div[@class="atc-vote-bts"]//span[@class="num"]').get()
        likes = remove_tags(like)
        # print("likes : ", likes)

        #댓글수 가져오기
        comment_cnt = response.xpath('//span[@class="ptCl num cmt-cnt-ori"]/text()').get()
        # print(comment_cnt)

        # 조회수 가져오기
        view = response.xpath('//ul[@class="ldd-title-under"]/li/span[@class="num"]').get()
        views = remove_tags(view)
        # print("views : ", views)

        #게시판 카테고리
        boardcategory = response.xpath('//header[@class="bBd-hd"]//a/text()').get()
        # print(boardcategory)

        #게시글 카테고리
        documentcategory = response.xpath('//span[@class="atc-ctg"]//a/text()').get()
        # print(documentcategory)


        MiniGigiKorea_data = {  'url':                       self.start_urls,
                                'site':                      self.site,
                                'document':                  document,
                                'documenttype':              np.NAN,
                                'postdate':                  date,
                                'likes' :                    likes,
                                'dislike' :                  np.NAN,
                                'comment_cnt' :              comment_cnt,
                                'views':                     views,
                                'boardcategory' :            boardcategory,
                                'documentcategory' :         documentcategory}
        # yield MiniGigiKorea_data
        df = pd.DataFrame([MiniGigiKorea_data])
        df.to_csv('MiniGigiKorea_data.csv', index=False, mode='a', header=not Path('MiniGigiKorea_data.csv').exists())

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(MiniGigiKoreaSpider, keyword='지니뮤직')
    process.start()