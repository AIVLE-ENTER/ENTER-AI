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

from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus import BaseDocTemplate, PageTemplate, KeepTogether, Frame

from project.utils.mermaid_utils import *
from project.server.modules.set_template import SetTemplate


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
        self.config         = SetTemplate(user_id).load('chatgpt','conversation')
        self.params         = SetTemplate(user_id)
    
    
    def load_history(self):
        if self.history_path.is_file():
            with open(self.history_path,'rb') as f:
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
        
        if not self.memory:
            self.memory = self.load_history()

        memory_k = self.memory_load_k(5)
        
        loaded_memory = RunnablePassthrough.assign(
            chat_history=RunnableLambda(memory_k.load_memory_variables) | itemgetter("history"),
        )
        
        if self.config.condense == '':
            condense_prompt = self.config.condense_default
            
        else:
            condense_prompt = self.config.condense
            
        CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([
                                                                    ("system", condense_prompt + ' conversation : {chat_history}'),
                                                                    ("human", "{question}"),
                                                                    ])

        # Now we calculate the standalone question
        standalone_question = {
            "standalone_question": {
                "question": lambda x: x["question"],
                "chat_history": lambda x: get_buffer_string(x["chat_history"]),
            }
            | CONDENSE_QUESTION_PROMPT
            | ChatOpenAI(temperature = 0,
                         model       = self.params.load('chatgpt','params').model
                         )
            | StrOutputParser(),
        }
        
        #3. 벡터DB에서 불러오기 : retrieved_documents 부분
        vectorstore = FAISS.load_local(folder_path = self.database_path, 
                                       embeddings  = OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()#(search_kwargs={"k": 50})

        retriever_from_llm = MultiQueryRetriever.from_llm(retriever = retriever, 
                                                          llm       = ChatOpenAI(model       = self.params.load('chatgpt','params').model,
                                                                                 temperature = 0))
        
        # Now we retrieve the documents
        retrieved_documents = {
            "docs": itemgetter("standalone_question") | retriever_from_llm,
            "question": lambda x: x["standalone_question"],
        }

        #4. 최종 답하는 부분 : answer 부분
        # context를 참조해 한국어로 질문에 답변하는 템플릿
        
        if self.config.system == '':
            answer_prompt = self.config.system_default
            
        else:
            answer_prompt = self.config.system
        
        ANSWER_PROMPT = ChatPromptTemplate.from_messages([
                                                        ("system", answer_prompt),
                                                        ("human", "{question}"),
                                                        ])
        
        if self.config.document == '':
            document_prompt = self.config.document_default
            
        else:
            document_prompt = self.config.document

        DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template=document_prompt)
  

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
                  "answer": final_inputs | ANSWER_PROMPT | ChatOpenAI(model=self.params.load('chatgpt','params').model),
                  #"docs": itemgetter("docs"),
                  }
        
        #5. 체인 연결
        final_chain = loaded_memory | standalone_question | retrieved_documents | answer
        
        return final_chain
    
    
    def conversation_json(self):
        if not self.memory:
            self.memory = self.load_history()
            
        temp = self.memory.load_memory_variables({})['history']
        n = len(temp)//2
        conversation = {'n': n, 'conversation':[]}
        
        for i in range(n):
            conversation['conversation'].append({'history_id': f'{self.user_id}_{self.keyword}_{i}',
                                                 'question':temp[2*i].content,
                                                 'answer': temp[2*i+1].content
                                                 })
            
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
          
            yield stream['answer'].content
            
        self.memory.save_context({"question" : query['question']}, {"answer" : self.stream_history})
        self.save_history()

    
class ReportChainPipeline():
        
    def __init__(self, 
                user_id:str, 
                keyword:str,
                ):
        self.BASE_DIR          = Path(__file__).parent.parent.parent / 'user_data' / user_id 
        self.database_path     = self.BASE_DIR / 'database' / keyword
        self.user_id           = user_id
        self.keyword           = keyword
        self.config            = SetTemplate(user_id)
        self.report_template   = ''
        self.document_template = ''
    
    def load_chain(self):
        
        vectorstore = FAISS.load_local(folder_path = self.database_path, 
                                       embeddings  = OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()#search_kwargs={"k": 10})

        retriever_from_llm = MultiQueryRetriever.from_llm(
                                                          retriever = retriever, 
                                                          llm       = ChatOpenAI(model       = self.config.load('chatgpt','params').model,
                                                                                 temperature = 0,
                                                                                 ))
        
        # Now we retrieve the documents
        config = self.config.params.load(self.BASE_DIR / 'template' / 'configs.yaml' ,addict=False)['chatgpt']['templates']['report']
        
        if config['prompt'] == '':
            self.report_template = config['prompt_default']
            
        else:
            self.report_template = config['prompt']
            
       
        if config['document'] == '':
            self.document_template = config['document_default']
            
        else:
            self.document_template = config['document']
        
        retrieved_documents = retriever_from_llm.get_relevant_documents(query=self.report_template)
        
        DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template=self.document_template)


        def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n"):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
           
            return document_separator.join(doc_strings)
        
        
        ANSWER_PROMPT = self.report_template.format(context = _combine_documents(retrieved_documents))
        answer_prompt = ChatPromptTemplate.from_messages([('system',"당신은 한국어로 보고서를 최대한 자세히 써야합니다"),
                                                          ('system',ANSWER_PROMPT),
                                                          ('human',"제목은 *, 소제목은 #, 하위 항목은 -로 시작하게 해줘")])

        print(answer_prompt.format_prompt().to_messages())
        result = ChatOpenAI(model=self.config.load('chatgpt','params').model).invoke(answer_prompt.format_prompt().to_messages()).content
        

        return self.to_pdf(result)
    
    
    def to_pdf(self,content):
        pdfmetrics.registerFont(TTFont("맑은고딕", "malgun.ttf"))
        pdfmetrics.registerFont(TTFont("맑은고딕B", "Malgunbd.ttf"))
        # text_frame = Frame(
        #     x1=2.54 * cm ,  # From left
        #     y1=2.54 * cm ,  # From bottom
        #     height=24.16 * cm,
        #     width=15.92 * cm,
        #     leftPadding=0 * cm,
        #     bottomPadding=0 * cm,
        #     rightPadding=0 * cm,
        #     topPadding=0 * cm,
        #     showBoundary=0,
        #     id='text_frame'
        # )

        content = convert_mm(content)
        lines = content.split('\n')
        L=[]

        for line in lines:
            if line == '':
                continue
            
            if "mermaid;" in line:
                image_mm(line,L)
                continue
            
            if line[0]=='*':
                L.append(Paragraph(line.replace('*','')+'<br/><br/>',ParagraphStyle(name='fd',fontName='맑은고딕B',fontSize=21,leading=40)))
                L.append(HRFlowable(width='100%', thickness=0.2))
                continue
            
            elif line[0]=='#':
                L.append(Paragraph(line.replace('#',''),ParagraphStyle(name='fd',fontName='맑은고딕B',fontSize=15,leading=30)))
                
            else:
                L.append(Paragraph(line+'<br/><br/>',ParagraphStyle(name='fd',fontName='맑은고딕',fontSize=12,leading=20)))
                
        #L.append(KeepTogether([]))
        
        self.mermaid(content,L)
        
        # doc = BaseDocTemplate(str(self.BASE_DIR / 'Report.pdf'), pagesize=A4)
        # frontpage = PageTemplate(id='FrontPage',
        #                      frames=[text_frame]
        #             )
        # doc.addPageTemplates(frontpage)
        # doc.build(L)
        
        return str(self.BASE_DIR / 'Report.pdf')
        
    
    def mermaid(self,content,L):
        answer_prompt = ChatPromptTemplate.from_messages([('system',"다음 보고서에서 Review of Statistics의 각 항목의 내용을 기반으로 충분히 mermaid 코드를 만듭니다. "),
                                                          ('human',content)])
        result = ChatOpenAI(model=self.config.load('chatgpt','params').model).invoke(answer_prompt.format_prompt().to_messages()).content
            
        result = convert_mm(result)
        lines = result.split('\n')

        for line in lines:
            if "mermaid;" in line:
                image_mm(line,L)
                    
        text_frame = Frame(
            x1=2.54 * cm ,  # From left
            y1=2.54 * cm ,  # From bottom
            height=24.16 * cm,
            width=15.92 * cm,
            leftPadding=0 * cm,
            bottomPadding=0 * cm,
            rightPadding=0 * cm,
            topPadding=0 * cm,
            showBoundary=0,
            id='text_frame'
        )
        L.append(KeepTogether([]))
        
        doc = BaseDocTemplate(str(self.BASE_DIR / 'Report.pdf'), pagesize=A4)
        frontpage = PageTemplate(id     = 'FrontPage',
                                 frames = [text_frame]
                    )
        
        doc.addPageTemplates(frontpage)
        doc.build(L)