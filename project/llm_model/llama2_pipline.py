import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class LlmPipeline():
    
    def __init__(self, model_path) -> None:
        
        self.model = AutoModelForCausalLM.from_pretrained(model_path,
                                                          device_map        = "auto",
                                                          trust_remote_code = False,
                                                          revision          = "main")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, 
                                                       use_fast = True)
    
    def load(self):
        pipe =  pipeline(
                    task                 = "text-generation",
                    model                = self.model,
                    tokenizer            = self.tokenizer,
                    torch_dtype          = torch.bfloat16,
                    device_map           = "auto",
                    max_new_tokens       = 5,
                    do_sample            = True,
                    top_k                = 30,
                    num_return_sequences = 1,
                    eos_token_id         = self.tokenizer.eos_token_id
        )
        
        return pipe
    
    def set_template(self, my_prompt):
        instruction = "User: {user_input}"
        my_prompt = """\
            You must distinguish among South Korea's mobile telecommunication companies (skt, kt, lg u+). 
            
            Provide answers with ONLY 'yes' or 'no'. no more answer
            """

        template = self._get_prompt(instruction, my_prompt)
        
        return template
    
    def _get_prompt(self, instruction, new_system_prompt) -> str:
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        
        SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
        prompt_template =  B_INST + SYSTEM_PROMPT + instruction + E_INST
        
        return prompt_template
    
    def cut_off_text(self, text:str, prompt):
        cutoff_phrase = prompt
        index = text.find(cutoff_phrase)
        
        if index != -1:
            return text[:index]
        else:
            return text

    def remove_substring(self, string:str, substring:str):
        
        return string.replace(substring, "")

    def generate(self, text):
        prompt = self._get_prompt(text)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            inputs = self.tokenizer(prompt, return_tensors="pt").to('cuda')
            outputs = self.model.generate(**inputs,
                                    max_new_tokens=512,
                                    eos_token_id=self.tokenizer.eos_token_id,
                                    pad_token_id=self.tokenizer.eos_token_id,
                                    )
            final_outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            final_outputs = self.cut_off_text(final_outputs, '</s>')
            final_outputs = self.remove_substring(final_outputs, prompt)

        return final_outputs#, outputs

    def parse_text(self, text):
            import textwrap
            wrapped_text = textwrap.fill(text, width=100)
            print(wrapped_text +'\n\n')
            # return assistant_text
            
    