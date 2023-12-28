from .xpath import Xpath
from .settings import CrawlerSettings

from os import walk
from pathlib import Path
from typing import List, Union

def search_files(dir_root:Union[str, Path], ext:str='.html') -> List[Path]:
    return [
        Path(root) / file
        for root, dirs, files in walk(dir_root)
        for file in files
        if file.endswith(ext) ]