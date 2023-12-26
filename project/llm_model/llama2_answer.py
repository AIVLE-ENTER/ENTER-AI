from langchain.chains import LLMChain 
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms.huggingface_pipeline import HuggingFacePipeline

from llm_model.llama2_pipline import LlmPipeline


class LangchainPipline():
    
    def __init__(self, 
                 model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"):
        
        self.pipe = LlmPipeline(model_path = model_path)
        
        self._my_prompt = \
            """
            You must distinguish among South Korea's mobile telecommunication companies (skt, kt, lg u+). 
            
            Provide answers with ONLY 'yes' or 'no'. no more answer
            """
            
    def chain(self, question):
        llm = HuggingFacePipeline(pipeline     = self.pipe.load(), 
                                  model_kwargs = {'temperature':0})

        prompt = PromptTemplate(
            input_variables = ["user_input"], 
            template        = self.get_prompt(self._my_prompt)
            )
        memory = ConversationBufferMemory(memory_key="chat_history")

        llm_chain = LLMChain(
                    llm     = llm,
                    prompt  = prompt,
                    verbose = True,
                    # memory=memory,
                    )

        return llm_chain.predict(user_input = question)
    
    @property
    def my_template(self):
        
        
        return self._my_prompt
    
    @my_template.setter
    def set_my_template(self, my_prompt):
        
        self._my_prompt = my_prompt
        
    def get_prompt(self, new_system_prompt) -> str:
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        
        SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
        prompt_template =  B_INST + SYSTEM_PROMPT + "User: {user_input}" + E_INST
        
        return prompt_template    
    
        
if __name__ == "__main__":
    model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"
    
    model_name = model_path.split('/')[-1]
    
    question = "'KT 인터넷은 어떰??' inputed text related LG U+???"
    # question = "hi"
    
    lp = LangchainPipline(model_path = model_path)
    # lp.set_my_template = 'you are a helpful assistant'
    
    print(lp.chain(question))
    
   

        
        