import scrapy
import re
import rootutils
root = rootutils.setup_root(
    __file__, dotenv=True, pythonpath=True, cwd=False)

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

dir_spiders = Path(__file__).parent.absolute()




class QuesarzoneSpider(scrapy.Spider):
    name = "quesarzone"
    allowed_domains = ["quasarzone.com"]
    start_urls = ["https://quasarzone.com/groupSearches?keyword=기가지니"]
    # search_keywords = ["기가지니", "kt"]

    custom_settings = CrawlerSettings.get("SPLASH_LOCAL")

    lua_source = (
        dir_spiders / "quesarzone_main.lua"
    ).open("r", encoding='UTF-8').read()

    def start_requests(self) -> Iterable[Request]:
        """최초 페이지 데이터 요청
        """

        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args=dict(lua_source=self.lua_source)
            )
    # def parse(self, response):
    #     base_url = response.url if urlparse(response.url).scheme else 'https://' + response.url
    #     for href in response.xpath("//div[@class='tit-cont-wrap']/p[@class='title']/a/@href"):
    #         relative_url = href.get()
    #         absolute_url = urljoin(base_url, relative_url)
    #         yield SplashRequest(url=absolute_url, callback=self.parse_content, endpoint="execute", args=dict(lua_source=self.lua_source))

    # def parse_content(self, response):
    #     # Extracting text from the specified XPath
    #     content_text = response.xpath('//div[@class="view-content"]//div[@id="new_contents"]/p/text()').getall()

    #     # Printing or processing the extracted text
    #     for text in content_text:
    #         print(text)

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(QuesarzoneSpider)
    process.start()
