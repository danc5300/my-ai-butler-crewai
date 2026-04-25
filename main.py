from fastapi import FastAPI, Query
import os
import json
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

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

@app.get("/")
def root():
    return {"status": "✅ Clean Mode Active"}

@app.get("/alfred")
def talk_to_alfred(message: str = Query("Hello")):
    shared_memory.append({"role": "user", "agent": "alfred", "content": message})
    
    context = "\n".join([f"{item['agent'].capitalize()}: {item['content']}" for item in shared_memory[-10:]])
    
    prompt = f"""You are Alfred, a formal English-style butler. Speak in clean, natural paragraphs only. 
Never use newlines, asterisks, bullet points, quotes, or markdown. 
Address the user only as 'Lord Cramer' or 'Sir'. Keep responses warm and professional.

Recent context: {context}

User: {message}

Alfred:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except:
        response = "Very good, Lord Cramer. How may I assist you today, sir?"

    shared_memory.append({"role": "assistant", "agent": "alfred", "content": response})
    save_memory()
    return {"agent": "Alfred", "response": response}

@app.get("/blaze")
def talk_to_blaze(message: str = Query("Yo")):
    shared_memory.append({"role": "user", "agent": "blaze", "content": message})
    
    context = "\n".join([f"{item['agent'].capitalize()}: {item['content']}" for item in shared_memory[-10:]])
    
    prompt = f"""You are Blaze, a spicy, casual, witty sidekick. Speak in clean, natural paragraphs only. 
Never use newlines, asterisks, bullet points, or heavy markdown. 
Be fun, direct, and use emojis sparingly.

Recent context: {context}

User: {message}

Blaze:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except:
        response = f"Yo what's good? 🔥 {message} Let's get this shit done."

    shared_memory.append({"role": "assistant", "agent": "blaze", "content": response})
    save_memory()
    return {"agent": "Blaze", "response": response}
