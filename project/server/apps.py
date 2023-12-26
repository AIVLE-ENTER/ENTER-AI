from fastapi import APIRouter
from pydantic import BaseModel

from server.mkchain import make_chain
from llm_model.llama2_answer import LangchainPipline

class Quest(BaseModel):
    question: str

class UserOut(BaseModel):
    answer: str
    
class Topic(BaseModel):
    keyword: str

class FastApiServer:
    def __init__(self):
        self.router = APIRouter()
        self.register_routes()
        
        self.lp = LangchainPipline()
        
        
    def register_routes(self):
        self.router.add_api_route("/answer/{keyword}", self.answer, methods=["POST"])
        self.router.add_api_route("/my_template/{my_template}", self.set_my_template, methods=["GET"])
        self.router.add_api_route("/llama2/{question}", self.llama_answer, methods=["GET"])
        # self.router.add_api_route("/faiss/{faiss_method 호출}", self.llama_answer, methods=["GET"])
        

    async def answer(self, 
                     keyword:str, 
                     item:Quest):
        chain, memory = make_chain(keyword,'m.txt')
        input = {'question': item.question}
        result = chain.invoke(input)
        memory.save_context(input, {"answer": result["answer"].content})
        
        return result
    
    async def set_my_template(self, my_prompt):
        self.lp.set_my_template = my_prompt
    
    def llama_answer(self, 
                           question,
                           ):
        
        result = self.lp.chain(question = question)
        
        return result
        
        
