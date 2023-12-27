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

    custom_settings = CrawlerSettings.get("SPLASH_LOCAL")

    lua_source = (
            dir_spiders / "quesarzone_main.lua"
        ).open("r", encoding='UTF-8').read()

    def start_requests(self) -> Iterable[Request]:
        """최초 페이지 데이터 요청
        """

        for url in self.start_urls:
            yield SplashRequest(
                url      = url,
                callback = self.parse_anything,
                endpoint = "execute",
                args     = dict(lua_source=self.lua_source)
            )

    url = []

    def parse_anything(self, response: TextResponse):
        for li in response.xpath("//*[@class='img-type']"):
            # print(li.xpath('string(.)').getall())
            print(Xpath(li).get_clean("a[@target='_blank']/@href"))
            # print(li.xpath("//a[@target='_blank']//@href").get())






if __name__ == '__main__':

    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(QuesarzoneSpider)
    process.start()