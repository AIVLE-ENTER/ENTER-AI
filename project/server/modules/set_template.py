import pyrootutils
pyrootutils.setup_root(search_from = __file__,
                       indicator   = "README.md",
                       pythonpath  = True)

import os
import shutil
import pandas as pd
from addict import Dict
from pathlib import Path

from project.utils.configs import ParamConfig 

class SetTemplate():
    # 메서드 별로 llama: crawl_company, crawl_product
    def __init__(self, 
                 user_id: str, 
                 ) -> None:
        
        self.user_id        = user_id
        self._BASE_SAVE_DIR = Path(__file__).parent.parent.parent / 'user_data' / user_id / 'template'
        self.params         = ParamConfig()

        
    @property
    def base_save_dir(self):
        
        return self._BASE_SAVE_DIR
    
    @base_save_dir.setter
    def set_base_dir(self, new_base_dir):
        
        self._BASE_SAVE_DIR = new_base_dir
    
    def load(self, llm:str, template_type:str):
        config = self.params.load(self.base_save_dir/ 'configs.yaml')
        
        # return {'status' : config[self.target_llm]['templates'][template_type]}
        return config[llm]['templates'][template_type]
    
    def load_template(self, llm:str, template_type:str):
        config = self.load(llm, template_type)
        
        return getattr(self,f'{template_type}_template')(config)
        
        
        
    def edit(self, **kwargs:Dict): # SetTemplate 초기화 시 입력한 llm을 통해 llama 또는 chatgpt template설정 가능. 
        config = self.params.load(self.base_save_dir / 'config.yaml')
        for key, item in kwargs.items():
            config[key] = item
        
        self.params.save(config, self.base_save_dir)
        
            
    # def check_llm_attr(self, target_llm):
    #     is_dir = [element.stem for element in self._BASE_SAVE_DIR.parent.parent.iterdir()]
    #     if target_llm in is_dir:
            
    #         return True
    #     else:    
            
    #         return {"status" : f'does not exist in the list. {is_dir}'}
        
        
    def crawl_template(self, kwargs:Dict) -> str: # 크롤러 분류 시 필요한 템플릿
            B_INST, E_INST = "[INST]", "[/INST]"
            B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
            
            defatul_key_bind = kwargs[llm]['templates']['crawl']
            
            if kwargs.system == '':
                system = kwargs.system_default
            else:
                system = kwargs.system
            
            if (kwargs.company_info == '') and (kwargs.product_info == ''):
                info_template = f"\n\n{kwargs.company_info_default}\n\n{kwargs.product_info_default}"
            else:
                info_template = f"\n\n{kwargs.company_info}\n\n{kwargs.product_info}"
                
            SYSTEM_PROMPT = B_SYS + system + info_template + E_SYS
            crawl_template =  B_INST + SYSTEM_PROMPT + "User: {user_input}" + E_INST
            
            return crawl_template
        
        
    def answer_template(self, kwargs:Dict): ## 다시 보기
        
        if (kwargs.prompt == '') and (kwargs.system == ''):
            system_prompt = kwargs.prompt_default
            
        else:
            system_prompt = kwargs.prompt
        
        converation_template =  system_prompt + ": {context}" + "\nQuestion: {question}"
        
        
        return converation_template
    
    
    def report_template(self, kwargs:Dict):
        if (kwargs.prompt == '') and (kwargs.system == ''):
            report_template = f"{kwargs.prompt_default}\n\n{kwargs.prompt_default}{kwargs.system_default}"
            
        else:
            report_template = f"{kwargs.prompt}\n\n{kwargs.system}"
            
        return report_template
                    
    
    def set_initial_templates(self,):
        
        dst = self.base_save_dir
        
        if dst.is_dir() == False:
            os.makedirs(name     = dst, 
                        exist_ok = True)
        
        init_config = self.params.load()
        self.params.save(init_config, dst)

        
if __name__ =="__main__":
    llm = 'chatgpt'
    # st = SetTemplate('star1234',)
    st = SetTemplate('star1234')
    # st.edit('안녕하세요')
    # st.edit(param_config()[f'{llm}_template'])
    # print(st.load_template())
    # st.set_initial_templates()
    a = ParamConfig().load('/home/wsl_han/aivle_project/remote/ENTER-AI/project/user_data/star1234/templates/config.yaml')
    print(a.chatgpt.templates.conversation.prompt_default)
    
    
    
    
    
    
        