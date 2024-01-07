import pyrootutils
project_root = pyrootutils.setup_root(search_from = __file__,
                                      indicator   = "README.md",
                                      pythonpath  = True)

import os
import time
import inspect
import subprocess
import pandas as pd
import importlib.util
from datetime import datetime

class CrawlManager():
    def __init__(self,
                 user_id: str,
                 keyword: str) -> None:

        self.user_id     = user_id
        self.keyword     = keyword.replace(" ","_")
        self.base_dir    = project_root / 'project' / 'user_data' / user_id / 'crawl_data' / self.keyword /datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        self.module_path = project_root / 'crawler' / 'crawler' / 'spiders'


    def run(self, except_spider:list[str]=[]):
        except_spider = ['PpomppuSpider'] + except_spider
        
        container_id = self.run_docker_splash()

        if self.base_dir.is_dir() == False:
            os.makedirs(self.base_dir, exist_ok=True)

        spider_command = self.get_spider_command(except_spider)
        self.run_scrapy(spider_command)
        self.remove_docker_container(container_id)
        self.merge_csv_files()


    @staticmethod
    def run_docker_splash():

        docker_command = "docker run -d -p 8050:8050 scrapinghub/splash"
        container_id = subprocess.check_output(docker_command, shell=True).strip().decode("utf-8")
        time.sleep(2)

        return container_id


    def run_scrapy(self, spider_command):
        subprocess.run(spider_command, shell=True, cwd=str(self.module_path.parent.parent))


    def remove_docker_container(self, container_id):

        stop_command = f"docker stop {container_id}"
        remove_command = f"docker rm {container_id}"

        subprocess.run(stop_command, shell=True)
        subprocess.run(remove_command, shell=True)


    def get_spider_command(self, except_spider):

        spiders = self._get_spider_name(except_spider)
        scrapy_command = ""
        for spider in spiders:
            scrapy_command += f"scrapy crawl {spider} -a user_id={self.user_id} -a keyword={self.keyword} -o {self.base_dir}/A_{spider.lower().split('spider')[0]}.csv \n"

        return scrapy_command


    def _get_spider_name(self, except_spider):

        spiders_list = []

        for modules in self.module_path.rglob('./*.py'):
            if (modules.name == '__init__.py') or (modules.name == None):
                continue

            spec = importlib.util.spec_from_file_location(modules.name, self.module_path / modules.stem / modules.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and ('Spider' in name):
                    spiders_list.append(name)

        return [item for item in spiders_list if item not in except_spider]


    def merge_csv_files(self):
        crawl_dir_list = list(self.base_dir.parent.iterdir())
        print(crawl_dir_list)

        for crawl_dir in crawl_dir_list:

            csv_files = list(crawl_dir.glob('A_*.csv'))
            # dataframes_list = [pd.read_csv(file) for file in csv_files if not pd.read_csv(file).empty()]

            dataframes_list = []
            for file in csv_files:
                try:
                    df = pd.read_csv(file)
                    if not df.empty:
                        dataframes_list.append(df)
                
                except pd.errors.EmptyDataError:
                    continue

            merged_df = pd.concat(dataframes_list)
            merged_df.to_csv(crawl_dir / 'merged_data.csv', index=False)

            for csv_file in csv_files:
                os.remove(csv_file)


if __name__ == "__main__":
    cm = CrawlManager('asdf1234', '레이니75')
    # print(cm.get_spider_command(except_spider=['PpomppuSpider']))
    cm.run()
