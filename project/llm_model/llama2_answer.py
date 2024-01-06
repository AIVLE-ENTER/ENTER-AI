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
                 model_path="mistralai/Mistral-7B-Instruct-v0.2"):
        
        self.model_path = model_path
        self.user_id    = user_id
        self.template   = SetTemplate(user_id)
        
        self.pipe = LlmPipeline(model_path = self.model_path,
                                user_id    = self.user_id)
        
        
                
    def chain(self, question):
        
        llm = HuggingFacePipeline(pipeline     = self.pipe.load(),
                                  model_kwargs = {'temperature':0})

        prompt = PromptTemplate(
            input_variables = ["user_input"], 
            template        = self.template.load_template('llama', 'crawl')
            )
        # memory = ConversationBufferMemory(memory_key="chat_history")

        llm_chain = LLMChain(
                    llm     = llm,
                    prompt  = prompt,
                    verbose = True,
                    # memory=memory,
                    )

        return llm_chain.predict(user_input=question)
    
        
if __name__ == "__main__":
    # model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"
    model_path = "mistralai/Mistral-7B-Instruct-v0.2"
    
    model_name = model_path.split('/')[-1]
    
    question = """5.21. 인터넷 방송인 성훈에게 유튜브 채널 테러 및 비난5.22. 2022년 클템, 김동준 해설 페이커 패싱 선동 사건5.23. SKT 마이너 갤러리 성명문 작성 및 2차 트럭 시위 사건5.24. T1악성팬 담원 기아 간담회 참석 인증 사건5.25. DRX 우승 폄하 사건5.26. 임재현 코치 과거사 왜곡 사건5.27. KT 프로게임단 마이너 갤러리 여론 조작 논란 5.28. T1 팬덤 및 단장의 ..."""
    # question = "hi"
    
  
    lp = LangchainPipline(user_id='asdf1234', model_path = model_path)
   
    print(lp.chain(question))
    