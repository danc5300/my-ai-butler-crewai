from fastapi import FastAPI, Query
import os
from langchain_openrouter import ChatOpenRouter

app = FastAPI(title="My AI Butler")

# LLM setup (lazy loaded)
llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    llm = ChatOpenRouter(
        model=os.getenv("MODEL", "deepseek/deepseek-chat"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
    )
    print("✅ OpenRouter connected successfully")

@app.get("/")
def root():
    return {
        "status": "✅ Server is LIVE",
        "alfred": "Ready",
        "blaze": "Ready",
        "openrouter": "Connected"
    }

@app.get("/alfred")
def talk_to_alfred(message: str = Query("Hello")):
    if not llm:
        return {"error": "LLM not ready yet"}
    # Simple response for now
    return {
        "agent": "Alfred",
        "response": f"Very good, Lord Cramer. {message} How may I assist you today, sir?"
    }

@app.get("/blaze")
def talk_to_blaze(message: str = Query("Yo")):
    if not llm:
        return {"error": "LLM not ready yet"}
    return {
        "agent": "Blaze",
        "response": f"Yo what's good? 🔥 {message} Let's get this shit done."
    }

print("✅ My AI Butler server started")
