import yaml
from addict import Dict
from pathlib import Path
from typing import Union, Optional

class ParamConfig():
    
    def __init__(self):
        self.INIT_CONFIG_PATH = Path(__file__).parent / 'configs.yaml'
        
                
    def load(self, 
             path:Optional[Union[str, Path]]=None,
             addict=True):
        
        if path == None:
            path = self.INIT_CONFIG_PATH
            
        
        with open(path, 'r',encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if addict == True:
            
            return Dict(data)
        else:
            
            return data
    
    def save(self, 
             src:Union[str, Path, Dict]=None,
             dst:Optional[Union[str, Path]]=None,
             endpoint = 'configs.yaml',
             addict   = False):
        
        if isinstance(src, (str, Path)):
            data = self.load(path   = src,
                             addict = addict)
            
            if src != None and dst == None:
                dst = src
        else:
            data = src.to_dict() if addict == False else src
            
        self._save(data, dst, endpoint)
        
    def _save(self, data, dst, endpoint):
        
        if isinstance(dst, str):
            dst = f"{dst}/{endpoint}"
            
        if isinstance(dst, Path):
            dst = dst / endpoint
        
        with open(dst, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, sort_keys=False, allow_unicode=True, )

        
if __name__ == '__main__':
    llm = 'llama'
    params = ParamConfig().load()
    
    temp = params[llm]['templates']['crawl']
    temp = temp.system_default
        