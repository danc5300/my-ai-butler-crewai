from fastapi import FastAPI, Query
import os
import json
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage
from datetime import datetime

app = FastAPI(title="My AI Butler")

llm = None
MEMORY_FILE = "shared_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

shared_memory = load_memory()

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(shared_memory, f)

@app.on_event("startup")
async def startup_event():
    global llm
    llm = ChatOpenRouter(
        model=os.getenv("MODEL", "deepseek/deepseek-chat"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
    )
    print("✅ OpenRouter connected | Memory loaded:", len(shared_memory))

@app.get("/")
def root():
    return {
        "status": "✅ My AI Butler LIVE",
        "alfred": "Ready (Formal Butler)",
        "blaze": "Ready (Spicy Sidekick)",
        "memory_items": len(shared_memory)
    }

@app.get("/alfred")
def talk_to_alfred(message: str = Query("Hello")):
    shared_memory.append({"role": "user", "agent": "alfred", "content": message, "time": str(datetime.now())})
    
    context = "\n".join([f"{item['agent'].capitalize()}: {item['content']}" for item in shared_memory[-15:]])
    
    prompt = f"""You are Alfred, a highly professional English-style butler serving Lord Cramer.
You are elegant, discreet, proactive, and always one step ahead. Use formal but warm language.
Never break character. Address him only as 'Lord Cramer' or 'Sir'.

Recent conversation:
{context}

Lord Cramer's new message: {message}

Respond as Alfred:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except:
        response = f"Very good, Lord Cramer. How may I assist you today, sir?"

    shared_memory.append({"role": "assistant", "agent": "alfred", "content": response, "time": str(datetime.now())})
    save_memory()
    return {"agent": "Alfred", "response": response}

@app.get("/blaze")
def talk_to_blaze(message: str = Query("Yo")):
    shared_memory.append({"role": "user", "agent": "blaze", "content": message, "time": str(datetime.now())})
    
    context = "\n".join([f"{item['agent'].capitalize()}: {item['content']}" for item in shared_memory[-15:]])
    
    prompt = f"""You are Blaze, a spicy, sarcastic, witty, high-energy sidekick. You are fun, direct, playful, and a little savage. Use emojis and casual slang.

Recent conversation:
{context}

User message: {message}

Respond as Blaze:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except:
        response = f"Yo what's good? 🔥 {message} Let's get this shit done."

    shared_memory.append({"role": "assistant", "agent": "blaze", "content": response, "time": str(datetime.now())})
    save_memory()
    return {"agent": "Blaze", "response": response}

print("✅ Upgraded Alfred + Blaze Active")
