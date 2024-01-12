import numpy as np
import pandas as pd
from google_play_scraper import app, Sort, reviews_all

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument('headless')

service = Service(executable_path=ChromeDriverManager().install())


class GooglePlay():
    def __init__(self,keyword):
        self.site = 'google_play'
        self.keyword = keyword
        self.url = f"https://play.google.com/store/search?q={self.keyword}&c=apps&hl=ko-KR"
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

        self.driver = webdriver.Chrome(service=service, 
                                       options=chrome_options)


    def crawl(self):
        self.driver.get(self.url)

        reviews=self.driver.find_elements(by=By.XPATH, value = '//a[@class="Qfxief"]')[0]
        href = reviews.get_attribute('href')
    
        google_reviews = reviews_all(
                                    href.split("=")[1],
                                    sleep_milliseconds=0,
                                    lang='ko',
                                    country='kr',
                                    sort=Sort.NEWEST
                                    )
        
        df_google = pd.DataFrame(np.array(google_reviews),columns=['review'])
        df_google = df_google.join(pd.DataFrame(df_google.pop('review').tolist()))
        
        reviews = df_google[['content', 'thumbsUpCount', 'at']]
        reviews.rename(columns={'content': 'document', 'thumbsUpCount': 'likes', 'at': 'postdate'}, inplace=True)
        
        google_reviews = pd.concat([self.data, reviews], axis=0)
        google_reviews['url'] = self.url
        google_reviews['site'] = self.site

        google_reviews.to_csv('google_reviews.csv', index=False)
        
        return reviews


if __name__ == '__main__':
    google = GooglePlay("지니뮤직")
    google_reviews=google.crawl()

    google.driver.quit()
