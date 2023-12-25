import torch
from langchain.chains import LLMChain 
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from llama2_pipline import LlmPipeline


class LangchainPipline():
    
    def __init__(self, 
                 my_prompt,
                 model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"):
        
        self.pipe = LlmPipeline(model_path = model_path)
        
        self.template  = self.pipe.set_template(my_prompt)
    
    def chain(self, question):
        llm = HuggingFacePipeline(pipeline     = self.pipe.load(), 
                                  model_kwargs = {'temperature':0})

        prompt = PromptTemplate(
            input_variables = ["user_input"], 
            template        = self.template
            )
        memory = ConversationBufferMemory(memory_key="chat_history")

        llm_chain = LLMChain(
                    llm     = llm,
                    prompt  = prompt,
                    verbose = True,
                    # memory=memory,
                    )

        return llm_chain.predict(user_input = question)
        
if __name__ == "__main__":
    model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"
    
    model_name = model_path.split('/')[-1]
    
    question = "'lg u+ 인터넷은 어떰??' inputed text related KT???"
    my_prompt = """\
    You must distinguish among South Korea's mobile telecommunication companies (skt, kt, lg u+). 
    
    Provide answers with ONLY 'yes' or 'no'. no more answer.
    """
    lp = LangchainPipline(my_prompt  = my_prompt, 
                          model_path = model_path)
    # print(lp.chain(question))
    
   

        
        