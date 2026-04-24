from fastapi import FastAPI
import os
from langchain_openrouter import ChatOpenRouter

app = FastAPI(title="My AI Butler")

llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    llm = ChatOpenRouter(
        model=os.getenv("MODEL", "deepseek/deepseek-chat"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
    )
    print("✅ OpenRouter LLM connected")

@app.get("/")
def root():
    return {
        "status": "✅ Server is running",
        "openrouter": "Connected",
        "message": "Alfred and Blaze ready for testing"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

print("✅ Minimal FastAPI server started")
