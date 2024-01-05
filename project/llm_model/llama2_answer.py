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
                 model_path="TheBloke/Llama-2-13B-Chat-GPTQ"):
        
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
    model_path = "TheBloke/Llama-2-13B-Chat-GPTQ"
    # model_path = "42MARU/GenAI-llama2-ko-en-dpo-13b-test3"
    
    model_name = model_path.split('/')[-1]
    
    question = """I use Skt Internet, but it's always disconnected and not good for playing games. Which of the three telecommunications companies do you like???"""
    # question = "hi"
    
  
    lp = LangchainPipline(user_id='asdf1234', model_path = model_path)
   
    print(lp.chain(question))
    