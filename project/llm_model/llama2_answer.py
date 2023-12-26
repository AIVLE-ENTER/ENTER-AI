from langchain.chains import LLMChain 
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms.huggingface_pipeline import HuggingFacePipeline

from llm_model.llama2_pipline import LlmPipeline
from server.modules.set_template import SetTemplate


class LangchainPipline():
    
    def __init__(self, 
                 model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"):
        
        self.pipe = LlmPipeline(model_path = model_path)
        self.template = SetTemplate('llama')
        
    def chain(self, question):
        llm = HuggingFacePipeline(pipeline     = self.pipe.load(), 
                                  model_kwargs = {'temperature':0})

        prompt = PromptTemplate(
            input_variables = ["user_input"], 
            template        = self.template.load_template()
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
    
    question = "'KT 인터넷은 어떰??' inputed text related LG U+???"
    # question = "hi"
    
    lp = LangchainPipline(model_path = model_path)
    # lp.set_my_template = 'you are a helpful assistant'
    
    print(lp.chain(question))
    