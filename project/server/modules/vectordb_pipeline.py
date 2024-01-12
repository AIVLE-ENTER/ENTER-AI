import shutil
import pandas as pd
from pathlib import Path
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import DataFrameLoader

class VectorPipeline():
    BASE_DIR = Path(__file__).parent.parent.parent / 'user_data'

    @classmethod
    def embedding_and_store(cls, 
                            data:pd.DataFrame,
                            user_id:str,
                            keyword:str, 
                            embedding, 
                            target_col:str='document'):
        
        kwd_db_path = cls.BASE_DIR / user_id / 'database' / f'{keyword}'  
        
        loader = DataFrameLoader(data_frame          = data, 
                                 page_content_column = target_col)
        docs = loader.load()
        vectorstore = FAISS.from_documents(documents = docs, 
                                           embedding = embedding)
        
        if kwd_db_path.is_dir():
            vectorstore_old = FAISS.load_local(folder_path = kwd_db_path, 
                                               embeddings  = embedding)
            vectorstore_old.merge_from(vectorstore)
            vectorstore_old.save_local(kwd_db_path)
            
        else:
            vectorstore.save_local(folder_path=kwd_db_path, 
                                   )
            
            
    @classmethod
    def delete_store_by_keyword(cls, 
                                user_id:str, 
                                keyword:str):
        
        database_path = cls.BASE_DIR / user_id / 'database' / keyword
        history_path  = cls.BASE_DIR / user_id / 'history' / keyword
            
        if (history_path.is_dir() == False) or (database_path.is_dir() == False):
            
            return {"status" : "abnormal delete request"}
        
        else:
            shutil.rmtree(str(database_path))
            shutil.rmtree(str(history_path))
            
            return {"status" : "delete success"}
        
        
if __name__ == "__main__":
    # VectorPipeline.delete_store_by_keyword('asdf1234', 'cafecopy')
    print(VectorPipeline.BASE_DIR)