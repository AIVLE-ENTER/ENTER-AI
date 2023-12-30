import os
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from langchain.embeddings import OpenAIEmbeddings

from server.modules.set_template import SetTemplate
from llm_model.llama2_answer import LangchainPipline
from server.modules.chain_pipeline import ChainPipeline
from server.modules.vectordb_pipeline import VectorPipeline


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
        
        self.router.add_api_route("/", self.chat_list, methods=["GET"])
        self.router.add_api_route("/history/{user_id}/{keyword}", self.history, methods=["GET"])
        self.router.add_api_route("/answer/{user_id}/{keyword}/{stream}", self.answer, methods=["POST"])
        self.router.add_api_route("/llama/{user_id}/{question}", self.llama_answer, methods=["GET"]) # 추후 크롤링 파이프라인에 맞게 재조정(url호출 시 파이프라인 진행)
        self.router.add_api_route("/start_crawl/{user_id}/{keyword}", self.start_crawl, methods=["GET"])
        self.router.add_api_route("/vectordb/{user_id}/{method}/{keyword}", self.manage_vectordb, methods=["GET"])
        self.router.add_api_route("/my_template/{user_id}/{llm}/{my_template}", self.set_my_template, methods=["GET"])
        
        # self.router.add_api_route("/faiss/{faiss_method 호출}", self.llama_answer, methods=["GET"])

    async def chat_list(self, user_id: str):
        
        chat_list_path = Path(__file__).parent.parent / 'user_data' / user_id / 'database'
        chatlist = os.listdir(chat_list_path)
        
        return chatlist
    
    async def answer(self,
                     user_id: str,
                     keyword: str, 
                     item: Quest,
                     stream: bool):
        
        chainpipe       = ChainPipeline(user_id = user_id, 
                                  keyword = keyword)
        history         = chainpipe.load_history()
        chain           = chainpipe.load_chain()
        response_input  = {'question': item.question}
        result          = chain.invoke(response_input)
        
        history.save_context(response_input, {"answer" : result["answer"].content})
        chainpipe.save_history()
        
        if stream == True:
            return StreamingResponse(content    = chainpipe.streaming(chain, response_input), 
                                     media_type = "text/event-stream")
        else:
            return result
    
    async def history(self, 
                      user_id, 
                      keyword:str):
        
        chainpipe = ChainPipeline(user_id = user_id,
                                  keyword = keyword)
        history_conversation = chainpipe.conversation_json()
        
        return history_conversation
    
    async def set_my_template(self, # llm에 따라 저장하는 템플릿 방식 나눔. (llama2, chatgpt)
                              llm,
                              user_id:str,
                              my_template):
        
        st = SetTemplate(user_id = user_id,
                         llm     = llm)
        st.edit(my_template)
        
        
    def llama_answer(self, 
                     user_id,
                     question,
                     ): # 임시. 테스트로 두고 크롤링 파이프라인 개발하면 삭제할 예정
        
        lp = LangchainPipline(user_id = user_id)
        result = lp.chain(question = question)
        
        return result
    
    
    def manage_vectordb(self, 
                        user_id: str, 
                        method,  # url에 method를 넣는게 아니라 http통신에서 method를 통해 가져오기
                        keyword: str):

        if method == 'delete':
            
            return VectorPipeline.delete_store_by_keyword(user_id = user_id,
                                                          keyword = keyword)

                    
    async def start_crawl(self,
                          user_id: str,
                          keyword: str):
        
        # 1. spider 일괄 실행하는 함수 제작(crawl_main()), keyword 함께 넘겨주기
        # 1-1. 구글 플레이스토어 리뷰
        # 1-2. 가능하면) 유튜브 영상 파싱
        # (bard에 유튜브url입력하면 영상 요약해줌. 근데 bard는 api제공 안됨. 유저들이 만든 라이브러리 써야함), 해당영상 댓글 
        
        # 2. scarpy에서 수집된 데이터 df로 저장 하는 로직(각 데이터프레임은 keyword+사이트명+날짜로 관리)
        
        # 3. 저장한 df불러오기 
        # 3-1 이때, df 컬럼 획일화.         
        
        # lp = LangchainPipline()
        # result = lp.chain(question = df['data'])
        
        import pandas as pd
        # 5. df 순차적으로 loop
        data = pd.read_excel('/home/wsl_han/aivle_project/remote/ENTER-AI/review_data/naver_review/naver_review_goldpig.xlsx')
        # 6. [loop] 임베딩 및 vectordb에 저장
        VectorPipeline.embedding_and_store(data = data,
                                           user_id = user_id,
                                           keyword = 'goldpig',
                                           target_col='리뷰',
                                           embedding=OpenAIEmbeddings(),
                                           ) # TODO: 벡터디비 만들 때 templates폴더 함께 만들어줘야함
        # VectorPipeline.embedding_and_store(data = data,
        #                                    user_id = user_id
        #                                    keyword = ''
        #                                    target_col=''
        #                                    embedding='',
        #                                    )
        
        pass
