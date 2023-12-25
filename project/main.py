from fastapi import FastAPI
import uvicorn

from server.url import FastApiServer

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

# 클래스 인스턴스 생성
server = FastApiServer()

# 라우터 추가
app.include_router(server.router)

if __name__ == "__main__":
    uvicorn.run("main:answer", host="0.0.0.0", port=8000, reload=True)
