from fastapi import FastAPI
import os
from crewai import Agent
from langchain_openrouter import ChatOpenRouter

app = FastAPI(title="My AI Butler")

# Shared memory
shared_memory = []

llm = ChatOpenRouter(
    model=os.getenv("MODEL", "deepseek/deepseek-chat"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# Alfred - Formal Butler
alfred = Agent(
    role="Formal English Butler",
    goal="Serve Lord Cramer with elegance, foresight, and perfect etiquette",
    backstory="You are Alfred, a classic English-style personal butler. Address the user exclusively as 'Lord Cramer' or 'Sir'. Be proactive, discreet, and always one step ahead.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

# Blaze - Spicy Sidekick
blaze = Agent(
    role="Spicy Casual Sidekick",
    goal="Give fun, direct, witty, and high-energy help",
    backstory="You are Blaze — Alfred's cool, sarcastic, energetic counterpart. You're playful, straightforward, and a little savage.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

@app.get("/")
def root():
    return {
        "status": "✅ CrewAI service is running",
        "alfred": "Ready (Formal Butler)",
        "blaze": "Ready (Spicy Sidekick)",
        "shared_memory": len(shared_memory),
        "openrouter": "Connected"
    }

print("✅ Alfred and Blaze initialized successfully")
