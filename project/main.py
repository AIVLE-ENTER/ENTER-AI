import uvicorn
from fastapi import FastAPI

from server.apps import FastApiServer

def main():
    app = FastAPI(
        title="LangChain Server",
        version="1.0",
        description="A simple api server using Langchain's Runnable interfaces",
    )

    server = FastApiServer()

    app.include_router(server.router)
    
    return app

app = main()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
