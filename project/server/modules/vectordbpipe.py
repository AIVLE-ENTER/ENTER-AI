from langchain.document_loaders import DataFrameLoader
from langchain.vectorstores import FAISS
from pathlib import Path
import os

def vetorizer(df,embedding,keyword,content='Document'):
    loader = DataFrameLoader(df,page_content_column=content)
    docs = loader.load()
    vectorstore = FAISS.from_documents(docs,embedding=embedding)
    
    path = Path(__file__).parent.parent.parent / 'data' / 'database' / f'{keyword}'    
    if os.path.isdir(path):
        vectorstore_old = FAISS.load_local(path,embedding)
        vectorstore_old.merge_from(vectorstore)
        vectorstore_old.save_local(path)
    else:
        vectorstore.save_local(path)