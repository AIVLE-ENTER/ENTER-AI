import scrapy
import re
import rootutils
root = rootutils.setup_root(
    __file__, dotenv=True, pythonpath=True, cwd=False)

from urllib.parse import urlparse, parse_qs

from typing import Iterable
from datetime import datetime

from pathlib import Path
from urllib.parse import urljoin
from urllib.parse import urlparse

import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import Request, TextResponse
from scrapy.utils.request import fingerprint

from utils import Xpath, CrawlerSettings

import requests
from bs4 import BeautifulSoup
from w3lib.html import remove_tags

dir_spiders = Path(__file__).parent.absolute()


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

class QuesarzoneSpider(scrapy.Spider):
    name = "quesarzone"
    custom_settings = CrawlerSettings.get("SPLASH_LOCAL")
    def __init__(self,keyword):
        super().__init__()
        self.keyword = keyword
        self.start_urls = [f"https://quasarzone.com/groupSearches?keyword={self.keyword}"]
        self.num_page = page_cnt(keyword)

    lua_source = (
        dir_spiders / "quesarzone_main.lua"
    ).open("r", encoding='UTF-8').read()



    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args={"lua_source": self.lua_source},
            )

    def parse(self, response):
       #for href in response.xpath('//div[@class="float-center"]/ul/li/a/@href'):
        for i in range(1, page_cnt(self.keyword)+1):
            url = f'https://quasarzone.com/groupSearches?keyword={self.keyword}&page={i}'

            # detail_url = href.get()
            # url = response.urljoin(detail_url)
            print("parse : ", url)
            yield SplashRequest(
                url=url,
                endpoint="execute",
                args={"lua_source": self.lua_source},
                meta={'url': url},
                callback=self.parse_content,
        )

    def parse_content(self, response):
            # print(1)
        page_url = response.url
        # print(page_url)

        for href in response.xpath('//p[@class="title"]/a/@href'):
            detail_url = href.get()
            post_url = response.urljoin(detail_url)
            # print("parse_content : ", post_url)
            yield SplashRequest(
                url=post_url,
                callback=self.parse_text,
                endpoint="execute",
                args=dict(lua_source=self.lua_source),
    #             meta={'page_url': page_url, 'post_url': post_url},
        )
    def parse_text(self, response):
        # titles = response.xpath('//div[@class="common-view-area"]/dl/dt/h1 | //h1[@class="title"]/text()').getall()
        # titles = response.xpath('//div[@class="common-view-area"]/dl/dt/h1').getall()
        titles = response.xpath('//h1[@class="title"]/text()').getall()



        for title in titles:
            title_text = remove_tags(title).strip()
            # title_text = re.sub(r'^\d+\s*', '', title_text).strip()
            # title_text = re.sub(r'\s{2,}', ' ', title_text).strip()
            title_text = re.sub(r'^\d+\s*|\s{2,}', ' ', title_text).strip()
            print(title_text)






            # 중복 체크 후 방문하지 않았다면 크롤링 수행
            # if url not in self.visited_urls:
            #     yield SplashRequest(
            #         url=url,
            #         endpoint="execute",
            #         args=dict(lua_source=self.lua_source),
            #         meta={'url': url},
            #         callback=self.parse_content,
            #     )
                # 크롤링한 URL을 방문한 URL 목록에 추가
                # self.visited_urls.add(url)

        # 다음 버튼을 찾아서 눌러 다음 페이지로 이동
        # next_button_href = response.xpath('//a[@class="page-jump next active"]/@href').get()

        # if next_button_href:
        #     next_button_url = response.urljoin(next_button_href)
        #     # print(f"Next Button URL: {next_button_url}")

        #     # 중복 체크 후 방문하지 않았다면 다음 페이지 크롤링 수행
        #     if next_button_url not in self.visited_urls:
        #         yield SplashRequest(
        #             url=next_button_url,
        #             endpoint="execute",
        #             args=dict(lua_source=self.lua_source),
        #             callback=self.parse,
        #         )
        #         # 다음 페이지로 이동한 URL을 방문한 URL 목록에 추가
        #         self.visited_urls.add(next_button_url)

    # def parse_detail(self, response):
    #     # Add your code for parsing the detail page here
    #     pass






# dict(
#     url              = None,  #Document의 url
#     site             = None,  # ,
#     document         = None,  #가져오는 게시글
#     documenttype     = None,  # [comment, app, post]
#     postdate         = None,  #게시된 날짜
#     likes            = None,  #{DocumentType}의 추천수(공감수)
#     dislike          = None,  #{DocumentType}비추천수
#     commentcnt       = None,  #댓글수
#     views            = None,  #조회수
#     boardcategory    = None,  #게시판 분류
#     documentcategory = None,) #게시글의 분류


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(QuesarzoneSpider, keyword='지니뮤직')
    process.start()
