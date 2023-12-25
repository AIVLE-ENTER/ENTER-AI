from fastapi import APIRouter
from pydantic import BaseModel

from server.mkchain import make_chain

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

    def register_routes(self):
        self.router.add_api_route("/answer/{keyword}", self.answer, methods=["POST"])

    async def answer(self, keyword:str, item:Quest):
        chain, memory = make_chain(keyword,'m.txt')
        input = {'question': item.question}
        result = chain.invoke(input)
        memory.save_context(input, {"answer": result["answer"].content})
        return result
