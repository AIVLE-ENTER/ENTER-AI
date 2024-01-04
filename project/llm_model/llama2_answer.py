import pyrootutils
pyrootutils.setup_root(search_from = __file__,
                       indicator   = "README.md",
                       pythonpath  = True)

from langchain.chains import LLMChain 
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms.huggingface_pipeline import HuggingFacePipeline

from project.llm_model.llama2_pipline import LlmPipeline
from project.server.modules.set_template import SetTemplate
from project.utils.configs import ParamConfig


class LangchainPipline():
    
    def __init__(self,
                 user_id,
                 model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"):
        
        self.model_path = model_path
        self.user_id    = user_id
        self.template   = SetTemplate(user_id)
        
        self.pipe = LlmPipeline(model_path = self.model_path,
                           user_id    = self.user_id)
        
        
                
    def chain(self, question):
        
        llm = HuggingFacePipeline(pipeline     = self.pipe.load(),#self.pipe.load(), # 이렇게 하니까 모델을 다시 로드하긴 하지만 메모리는 정상적으로 차지함 
                                  model_kwargs = {'temperature':0})

        prompt = PromptTemplate(
            input_variables = ["user_input"], 
            template        = self.template.load_template('llama', 'crawl')
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
    
    question = "skt 인터넷 속도도 빠르고 서비스도 괜찮은듯 내가 원래 lg 인터넷 썼는데 맨날 끊겼음 \
                근데 skt로 바꾸니까 끊기는게 덜하고 특히 해외서버에 있는 게임 할 때 끊기는게 잘 없음"
    # question = "hi"
    
  
    lp = LangchainPipline(user_id='asdf1234', model_path = model_path)
   
    print(lp.chain(question))
    