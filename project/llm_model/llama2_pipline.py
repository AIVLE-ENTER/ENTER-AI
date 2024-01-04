import pyrootutils
pyrootutils.setup_root(search_from = __file__,
                       indicator   = "README.md",
                       pythonpath  = True)
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from project.utils.configs import ParamConfig
from project.server.modules.set_template import SetTemplate

class LlmPipeline():
    
    def __init__(self, model_path, user_id) -> None:
        
        self.model = AutoModelForCausalLM.from_pretrained(model_path,
                                                          device_map        = "auto",
                                                          trust_remote_code = False,
                                                          revision          = "main")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, 
                                                       use_fast=True)
        
              
        self.config = ParamConfig().load(Path(__file__).parent.parent / 'user_data' / user_id / 'template' / 'configs.yaml')
        
        
        
    
    def load(self):
        pipe =  pipeline(
                    task                 = "text-generation",
                    model                = self.model,
                    tokenizer            = self.tokenizer,
                    torch_dtype          = torch.bfloat16,
                    device_map           = "auto",
                    do_sample            = True,
                    eos_token_id         = self.tokenizer.eos_token_id,
                    **self.config.llama.params
                    )
        
        return pipe
      
    
    
    # def cut_off_text(self, text:str, prompt):
    #     cutoff_phrase = prompt
    #     index = text.find(cutoff_phrase)
        
    #     if index != -1:
    #         return text[:index]
    #     else:
    #         return text

    # def remove_substring(self, string:str, substring:str):
        
    #     return string.replace(substring, "")

    # def generate(self, text):
    #     prompt = self._get_prompt(text)
    #     with torch.autocast('cuda', dtype=torch.bfloat16):
    #         inputs = self.tokenizer(prompt, return_tensors="pt").to('cuda')
    #         outputs = self.model.generate(**inputs,
    #                                 max_new_tokens=512,
    #                                 eos_token_id=self.tokenizer.eos_token_id,
    #                                 pad_token_id=self.tokenizer.eos_token_id,
    #                                 )
    #         final_outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    #         final_outputs = self.cut_off_text(final_outputs, '</s>')
    #         final_outputs = self.remove_substring(final_outputs, prompt)

    #     return final_outputs#, outputs

    # def parse_text(self, text):
    #         import textwrap
    #         wrapped_text = textwrap.fill(text, width=100)
    #         print(wrapped_text +'\n\n')
            # return assistant_text
            
    