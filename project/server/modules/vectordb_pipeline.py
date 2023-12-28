import shutil
import pandas as pd
from pathlib import Path
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import DataFrameLoader

class VectorPipeline():
    
    def __init__(self) -> None:
        self.BASE_DIR = Path(__file__).parent.parent

    
    def embedding_and_store(self, 
                            data:pd.DataFrame, 
                            embedding, 
                            keyword:str, 
                            content:str = 'document'):
        
        kwd_db_path = self.BASE_DIR.parent / 'data' / 'database' / f'{keyword}'  
        
        loader = DataFrameLoader(data, 
                                 page_content_column = content)
        docs = loader.load()
        vectorstore = FAISS.from_documents(docs, 
                                           embedding = embedding)
        
        if kwd_db_path.is_dir():
            vectorstore_old = FAISS.load_local(kwd_db_path, 
                                               embedding)
            vectorstore_old.merge_from(vectorstore)
            vectorstore_old.save_local(kwd_db_path)
            
        else:
            vectorstore.save_local(kwd_db_path)
            
    def delete_store_by_keyword(self, keyword):
        
        database_path = self.BASE_DIR / 'data' / 'database' / f'{keyword}'
        history_path  = self.BASE_DIR / 'data' / 'history' / f'{keyword}.pkl'
            
        if not history_path.is_file() or not database_path.is_file():
            
            return {"status" : "abnormal delete request"}
        
        else:
            shutil.rmtree(database_path)
            history_path.unlink()
            
            return {"status" : "delete success"}