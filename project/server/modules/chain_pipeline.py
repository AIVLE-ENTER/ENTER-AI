import pyrootutils
pyrootutils.setup_root(search_from = __file__,
                       indicator   = "README.md",
                       pythonpath  = True)

import os
import pickle
from pathlib import Path
from operator import itemgetter

from langchain.chat_models import ChatOpenAI
from langchain.schema import format_document
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate, ChatPromptTemplate

from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from project.server.modules.set_template import SetTemplate

# TODO: 리뷰 8개만 참고함. 임베딩 시 또는 훑을 때 어떻게 되는지 봐야함

class ChainPipeline():
    
    def __init__(self, 
                 user_id:str, 
                 keyword:str):
        self.BASE_DIR       = Path(__file__).parent.parent.parent / 'user_data' / user_id 
        self.history_path   = self.BASE_DIR / 'history' / keyword / f'{keyword}.pkl'
        self.database_path  = self.BASE_DIR / 'database' / keyword
        self.memory         = None
        self.user_id        = user_id
        self.keyword        = keyword
        self.stream_history = None
        self.config         = SetTemplate(user_id)
    
    def load_history(self):
        if self.history_path.is_file():
            with open(self.history_path,'rb') as f: #경로예시 : ./data/history/m.txt
                memory = pickle.load(f)
        else:
            memory = ConversationBufferMemory(
                return_messages = True, 
                output_key      = "answer", 
                input_key       = "question"
                )
            
        self.memory = memory
        
        return memory
    
    
    def save_history(self):
        if self.history_path.is_file() == False:
            os.makedirs(self.history_path.parent, exist_ok=True)
            
        with open(self.history_path,'wb') as f:
            pickle.dump(self.memory,f)


    def load_chain(self):
        #stream_it = AsyncIteratorCallbackHandler()
        chain_path = self.BASE_DIR / 'template' / 'chatgpt' 
        
        if not self.memory:
            self.memory = self.load_history()
        # 1. 채팅 기록 불러오기 : loaded_memory 부분
        # 기록있으면 불러오고 없으면 비어있는 ConversationBufferMemory 생성
        memory_k = self.memory_load_k(5)
        
        loaded_memory = RunnablePassthrough.assign(
            chat_history=RunnableLambda(memory_k.load_memory_variables) | itemgetter("history"),
        )
        #print(memory_k.load_memory_variables({}))
        #print(len(memory_k.load_memory_variables({})['history']))
        #2. 채팅기록과 현재 입력으로 새로운 입력 생성  : standalone_question 부분
        # chat_history와 현재 question을 이용해 질문 생성하는 템플릿
        # _template = """Given the following conversation and a follow up Input, rephrase the follow up Input to be a standalone Input, in its original language.

        # Chat History: {chat_history}
        # Follow Up Input: {question}
        
        # Standalone question:"""
        print('standalone_template :',self.config.load('chatgpt','report').system_default)
        CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([
            ("system",self.config.load('chatgpt','report').system_default),
            ("human", "{question}"),
        ])
        
        # PromptTemplate.from_template(_template)

        # Now we calculate the standalone question
        standalone_question = {
            "standalone_question": {
                "question": lambda x: x["question"],
                "chat_history": lambda x: get_buffer_string(x["chat_history"]),
            }
            | CONDENSE_QUESTION_PROMPT
            | ChatOpenAI(temperature=0)
            | StrOutputParser(),
        }
        
        #3. 벡터DB에서 불러오기 : retrieved_documents 부분
        vectorstore = FAISS.load_local(folder_path = self.database_path, 
                                       embeddings  = OpenAIEmbeddings()) #./data/database/faiss_index
        retriever = vectorstore.as_retriever()#(search_kwargs={"k": 50})

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever = retriever, 
            llm       = ChatOpenAI(temperature = 0,
                                   #model       = self.params.model),)
            ))
        # Now we retrieve the documents
        retrieved_documents = {
            "docs": itemgetter("standalone_question") | retriever_from_llm,
            "question": lambda x: x["standalone_question"],
        }

        #4. 최종 답하는 부분 : answer 부분
        # context를 참조해 한국어로 질문에 답변하는 템플릿
        #보고서
        print('report template :', self.config.load_template('chatgpt','report'))
        ANSWER_PROMPT = ChatPromptTemplate.from_messages([
            ("system", self.config.load_template('chatgpt','report')),
            ("human", "{question}"),
        ])
        #print(p.prompt_default+p.system_default)
        
        #대화
        # p = x.load('conversation')
        # ANSWER_PROMPT = ChatPromptTemplate.from_messages([
        #     ("system", p.prompt_default+p.system_default),
        #     ("human", "{question}"),
        # ])
        # print(p.prompt_default+p.system_default)

        DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template=self.config.load_template('chatgpt','document'))


        def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            print(doc_strings)
            return document_separator.join(doc_strings)

        # Now we construct the inputs for the final prompt
        final_inputs = {
            "context": lambda x: _combine_documents(x["docs"]),
            "question": itemgetter("question"),
        }
        # And finally, we do the part that returns the answers
        answer = {
            "answer": final_inputs | ANSWER_PROMPT | ChatOpenAI(),#streaming=True,callbacks=[stream_it]),    #streaming?
            #"docs": itemgetter("docs"),
        }
        
        #5. 체인 연결
        # And now we put it all together!
        final_chain = loaded_memory | standalone_question | retrieved_documents | answer
        
        return final_chain
    
    
    def conversation_json(self):
        if not self.memory:
            self.memory = self.load_history()
            
        temp = self.memory.load_memory_variables({})['history']
        n=len(temp)//2
        conversation = {'n': n, 'conversation':[]}
        
        for i in range(n):
            conversation['conversation'].append({'history_id': f'{self.user_id}_{self.keyword}_{i}',
                                                 'question':temp[2*i].content,
                                                 'answer': temp[2*i+1].content
                                                 })
        #j = json.dumps(d,ensure_ascii=False, indent=3)
        return conversation


    def memory_load_k(self, k:int):
        if not self.memory:
            self.memory = self.load_history()
            
        temp = self.memory.load_memory_variables({})['history']
        #print(temp)
        N_con = len(temp)//2
        
        if k >= N_con:
            return self.memory
        else:
            memory_k = ConversationBufferMemory(return_messages = True, 
                                                output_key      = "answer", 
                                                input_key       = "question")
            for i in range(N_con-k, N_con):
                memory_k.save_context({"question": temp[2 * i].content},
                                      {"answer": temp[2 * i+1].content})
            
            return memory_k
        
        
    async def streaming(self, chain, query):
        self.stream_history=''
        async for stream in chain.astream(query):
            self.stream_history += stream['answer'].content
            #print(self.stream_history)
            yield stream['answer'].content
        self.memory.save_context({"question" : query['question']}, {"answer" : self.stream_history})
        self.save_history()
        #print({"question" : query['question'], "answer" : self.stream_history})