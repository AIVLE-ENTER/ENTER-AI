import pandas as pd
from pathlib import Path

class SetTemplate():
    
    def __init__(self, llm) -> None:
        
        self.target_llm = llm
        self._BASE_SAVE_DIR = Path(__file__).parent.parent.parent / 'data' / 'templates' / llm / f'{llm}_template.txt'
        self.check_llm_attr(llm)
        
    @property
    def base_save_dir(self):
        
        return self._BASE_SAVE_DIR
    
    @base_save_dir.setter
    def set_base_dir(self, new_base_dir):
        
        self._BASE_SAVE_DIR = new_base_dir
        
    def edit(self, new_prompt_template): # SetTemplate 초기화 시 입력한 llm을 통해 llama 또는 chatgpt template설정 가능. 

        my_template = getattr(self, f'_{self.target_llm}_template')(new_prompt_template)
        self._save_template(my_template=my_template)
            
    def check_llm_attr(self, target_llm):
        is_dir = [element.stem for element in self._BASE_SAVE_DIR.parent.parent.iterdir()]
        if target_llm in is_dir:
            return True
        else:    
            raise ValueError(f'not in {is_dir}')
        
    def _llama_template(self, new_system_prompt) -> str: # 크롤러 분류 시 필요한 메서드
            B_INST, E_INST = "[INST]", "[/INST]"
            B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
            
            SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
            prompt_template =  B_INST + SYSTEM_PROMPT + "User: {user_input}" + E_INST
            
            return prompt_template
        
    # def _chatgpt_template(self, new_system_prompt):
    #     pass
    
    def _save_template(self, my_template):
        with open(self._BASE_SAVE_DIR, "w") as file:
            file.write(my_template)
    
    def load_template(self,):
        with open(self._BASE_SAVE_DIR, "r") as file:
            template = file.read()
            
        return template
    
if __name__ =="__main__":
    st = SetTemplate('llama')
    # st.edit('안녕하세요')
    print(st.load_template())
    
    
    
    
        