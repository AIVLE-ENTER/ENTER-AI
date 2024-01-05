import rootutils
root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=False)

import pyrootutils
project_root = pyrootutils.setup_root(search_from = __file__,
                                      indicator   = "README.md",
                                      pythonpath  = True)

import re
import scrapy
import pandas as pd
from pathlib import Path
from scrapy_splash import SplashRequest
from datetime import datetime

# 스파이더의 작업 디렉토리를 설정
dir_spiders = Path(__file__).parent.absolute()

class PpomppuSpider(scrapy.Spider):
    name = 'PpomppuSpider'
    user_agent = 'Mozilla/5.0'

    def __init__(self, user_id, keyword:str):

        super().__init__()
        self.site        = '뽐뿌'
        self.keyword     = keyword
        self.start_urls  = [f"https://www.ppomppu.co.kr/search_bbs.php?bbs_cate=2&keyword={self.keyword}"]
        self.url         = 'https://www.ppomppu.co.kr'
        self.url_counter = 0
        self.data        = pd.DataFrame(columns=[
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
        dir_spiders / "Ppomppu_main.lua").open("r", encoding='UTF-8'
        ).read()


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.page_cnt,
                endpoint="execute",
                args={"lua_source": self.lua_source},
            )


    def page_cnt(self, response):
        page_numbers = response.xpath('//div[@class="page"]/a[contains(@href, "page_no")]/@href').getall()

        if not page_numbers:
            url = f'https://www.ppomppu.co.kr/search_bbs.php?bbs_cate=2&keyword={self.keyword}'
            # print('url : ', url)
        else:
            last_page_numbers = [int(re.search(r'page_no=(\d+)', href).group(1)) for href in page_numbers]
            last_page_number = max(last_page_numbers)
            # print('last_page_number : ', last_page_number)

            for i in range(1, last_page_number+1):
                url = f"https://www.ppomppu.co.kr/search_bbs.php?search_type=sub_memo&page_no={i}&keyword={self.keyword}&page_size=20&bbs_id=&order_type=date&bbs_cate=2"
                # print('url : ' ,url)
                # print()
                yield SplashRequest(url,
                                    callback=self.parse,
                                    endpoint="execute",
                                    args={"lua_source": self.lua_source})

    def parse(self, response):
        for href in response.xpath('//span[@class="title"]/a/@href'):
            detail_url = href.get()
            post_url = response.urljoin(detail_url)
            # print("post_url : ", post_url)
            # print()
            yield SplashRequest(
                url=post_url,
                callback=self.parse_text,
                endpoint="execute",
                args=dict(lua_source=self.lua_source),
            )
        # title = 'https://www.ppomppu.co.kr' + response.xpath('//span[@class="title"]/a/@href').get()
        # print("title_url : " ,title)
        # print()

    def parse_text(self, response):
        # documentcategory = response.xpath('//div[@class="sub-top-text-box"]/font[@class="view_cate"]//text()').get()
        # print(documentcategory)



        # 조회수
        views = response.xpath('//div[@class="sub-top-text-box"]/font[@class="view_cate"]//text()').get()
        print(views)

        # 게시글
        # documents = response.xpath('//td/p').getall()
        # # print(response)
        # print("documents : " , documents)
        # print()


        # Ppomppu_data =  {   'url':                     self.url,
        #                     'site':                    self.site,
        #                     'document':                document,
        #                     'documenttype':            np.NAN,
        #                     'postdate':                date,
        #                     'likes' :                  ,
        #                     'dislike' :                np.NAN,
        #                     'comment_cnt' :            comment_cnt,
        #                     'views':                   views,
        #                     'boardcategory' :          ,
        #                     'documentcategory' :       }
        
        # tempCodeRunnerFile -> //td[@class="han"]/div[@class="sub-top-contents-box"]//div[@class="sub-top-text-box"]/font[@class="view_cate"]/text()
if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(PpomppuSpider, keyword='지니뮤직')
    process.start()
