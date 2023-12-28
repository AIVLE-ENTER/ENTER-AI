from parsel import Selector
from bs4 import BeautifulSoup

from scrapy.http import Response, TextResponse
from scrapy.selector.unified import SelectorList

class Xpath:

    # Element 관련
    def __init__(self, element:TextResponse):
        self.element = element


    def xpath(self, xpath):
        return Xpath(self.element.xpath(xpath))

    @property
    def html(self):
        if isinstance(self.element, Response):
            html =  self.element.body
        elif isinstance(self.element, (Selector, SelectorList)):
            html = "\n".join(self.element.re(".+"))
        return BeautifulSoup(html, 'lxml').prettify()

    @property
    def e(self):
        return self.element

    @property
    def children(self):
        return self.element.xpath("*")

    # 문자 추출 관련
    def get(self, xpath):
        return self.xpath(xpath).element.get()

    def get_clean(self, xpath):
        return self.clean_str(self.get(xpath))

    def getall(self, xpath):
        return self.xpath(xpath).element.getall()

    def getall_as_string(self, xpath):
        return [
            self.clean_str(
                e.xpath("string(.)").get())
            for e in self.xpath(xpath).element]

    def getall_as_string_joined(self, xpath, delimiter="\n"):
        return delimiter.join(self.getall_as_string(xpath))

    @staticmethod
    def clean_str(txt):
        if txt == None:
            return ""
        return (txt.replace("\n", "")
                .replace("\t","")
                .replace("\xa0", " ")
                .strip())

    # Loop 관련
    def zip(self, xpath1, xpath2):
        return zip(self.xpath(xpath1), self.xpath(xpath2))
