from fastapi import APIRouter
from pydantic import BaseModel

from server.modules.mkchain import make_chain
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
        self.router.add_api_route("/my_template/{llm}/{my_template}", self.set_my_template, methods=["GET"])
        self.router.add_api_route("/llama2/{question}", self.llama_answer, methods=["GET"]) # 추후 크롤링 파이프라인에 맞게 재조정(url호출 시 파이프라인 진행)
        self.router.add_api_route("/start_crawl/{keyword}", self.start_crawl, methods=["GET"]) 
        
        # self.router.add_api_route("/faiss/{faiss_method 호출}", self.llama_answer, methods=["GET"])
        

    async def answer(self, 
                     keyword:str, 
                     item:Quest):
        chain, memory = make_chain(keyword,'m.txt')
        input = {'question': item.question}
        result = chain.invoke(input)
        memory.save_context(input, {"answer": result["answer"].content})
        
        return result
    
    async def set_my_template(self, llm, my_prompt): 
        # property 오버라이딩? 저장해서 관리하는 방식? -> 저장 쪽으로 좀 더 쏠리는중
        # llm에 따라 저장하는 템플릿 방식 나눔.
        # llama2, chatgpt
        
        pass
    
    def llama_answer(self, 
                    question,
                    ): # 임시. 테스트로 두고 크롤링 파이프라인 개발하면 삭제할 예정
        
        result = self.lp.chain(question = question)
        
        return result
        
    async def start_crawl(self, keyword):
        # 1. spider 일괄 실행하는 함수 제작(crawl_main()), keyword 함께 넘겨주기
        # 1-1. 구글 플레이스토어 리뷰
        # 1-2. 가능하면) 유튜브 영상 파싱, 해당영상 댓글 
        
        # 2. scarpy에서 수집된 데이터 df로 저장 하는 로직(각 데이터프레임은 keyword+사이트명+날짜로 관리)
        
        # 3. 저장한 df불러오기 
        # 3-1 이때, df 컬럼 획일화. 
        
        # 4. llama2 모델로드를 그냥 여기서 할까 생각중..
        
        # lp = LangchainPipline()
        # result = self.lp.chain(question = df['data'])
        
        # 5. df 순차적으로 loop
        
        # 6. [loop] 임베딩 및 vectordb에 저장
        
        
        
        
        
        pass
