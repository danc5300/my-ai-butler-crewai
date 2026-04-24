from fastapi import FastAPI, Query
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

shared_memory = []

@app.get("/")
def root():
    return {
        "status": "✅ Server is LIVE",
        "alfred": "Ready (Formal Butler)",
        "blaze": "Ready (Spicy Sidekick)",
        "memory_items": len(shared_memory)
    }

@app.get("/alfred")
def talk_to_alfred(message: str = Query("Hello")):
    shared_memory.append({"role": "user", "agent": "alfred", "content": message})
    
    prompt = f"""You are Alfred, a formal English-style butler. Address the user only as 'Lord Cramer' or 'Sir'. 
    Speak elegantly, professionally, and proactively. Keep responses concise but helpful.

    User: {message}
    Alfred:"""
    
    try:
        response = llm.invoke(prompt).content.strip()
    except:
        response = f"Very good, Lord Cramer. How may I assist you with '{message}' today, sir?"
    
    shared_memory.append({"role": "assistant", "agent": "alfred", "content": response})
    return {"agent": "Alfred", "response": response}

@app.get("/blaze")
def talk_to_blaze(message: str = Query("Yo")):
    shared_memory.append({"role": "user", "agent": "blaze", "content": message})
    
    prompt = f"""You are Blaze, a spicy, casual, witty, and energetic sidekick. Be fun, direct, sarcastic, and high-energy. Use emojis.

    User: {message}
    Blaze:"""
    
    try:
        response = llm.invoke(prompt).content.strip()
    except:
        response = f"Yo what's good? 🔥 {message} Let's get this shit done."
    
    shared_memory.append({"role": "assistant", "agent": "blaze", "content": response})
    return {"agent": "Blaze", "response": response}

print("✅ Full Alfred + Blaze with LLM ready")
