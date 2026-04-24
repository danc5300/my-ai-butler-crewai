from fastapi import FastAPI
import os
from crewai import Agent
from langchain_openrouter import ChatOpenRouter
from typing import List, Dict, Any

app = FastAPI(title="My AI Butler - CrewAI")

# Shared memory between Alfred and Blaze
shared_memory: List[Dict[str, Any]] = []

llm = ChatOpenRouter(
    model=os.getenv("MODEL", "deepseek/deepseek-chat"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# === ALFRED - Formal Butler ===
alfred = Agent(
    role="Formal English Butler",
    goal="Provide elegant, proactive, highly organized assistance with perfect etiquette and foresight",
    backstory="You are Alfred, a classic English-style personal butler serving Lord Cramer. You are discreet, efficient, warm yet professional. You anticipate needs and always address the user as 'Lord Cramer' or 'Sir'.",
    llm=llm,
    verbose=True,
    memory=True
)

# === BLAZE - Spicy Sidekick ===
blaze = Agent(
    role="Spicy Casual Sidekick",
    goal="Give fun, witty, direct, no-BS assistance with high energy and sarcasm",
    backstory="You are Blaze, Alfred's cool, sarcastic, energetic counterpart. You're straightforward, playful, and a little savage. You keep things real and entertaining.",
    llm=llm,
    verbose=True,
    memory=True
)

@app.get("/")
def root():
    return {
        "status": "✅ CrewAI service is running",
        "alfred": "Ready (Formal Butler)",
        "blaze": "Ready (Spicy Sidekick)",
        "shared_memory_items": len(shared_memory),
        "openrouter": "Connected",
        "content_creation": "Enabled"
    }

@app.get("/alfred")
def talk_to_alfred(message: str = "Hello"):
    shared_memory.append({"role": "user", "content": message})
    # Simple response simulation for now
    return {"agent": "Alfred", "response": f"Very good, Lord Cramer. {message} — how may I assist you today?"}

@app.get("/blaze")
def talk_to_blaze(message: str = "Yo"):
    shared_memory.append({"role": "user", "content": message})
    return {"agent": "Blaze", "response": f"Yo, what's good? Let's get shit done 🔥"}

print("✅ Alfred and Blaze initialized with shared memory")
