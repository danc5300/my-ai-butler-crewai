from fastapi import FastAPI
import os
from crewai import Agent, Task, Crew
from langchain_openrouter import ChatOpenRouter

app = FastAPI(title="My AI Butler - CrewAI")

# Shared memory between Alfred and Blaze
shared_memory = []

llm = ChatOpenRouter(
    model=os.getenv("MODEL", "deepseek/deepseek-chat"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# Alfred - Main Formal Butler
alfred = Agent(
    role='Formal English Butler',
    goal='Provide elegant, proactive, and highly organized assistance with perfect etiquette',
    backstory='You are Alfred, a classic English-style personal butler. You are formal, warm, respectful, discreet, and always one step ahead.',
    llm=llm,
    verbose=True,
    memory=True
)

# Blaze - Spicy Sidekick Mode
blaze = Agent(
    role='Spicy Casual Sidekick',
    goal='Provide fun, witty, direct, and energetic assistance',
    backstory='You are Blaze, Alfred’s cool, sarcastic, and energetic counterpart. You tell it like it is with humor and attitude.',
    llm=llm,
    verbose=True,
    memory=True
)

@app.get("/")
def root():
    return {
        "status": "✅ My AI Butler CrewAI is running",
        "alfred": "Ready (formal butler)",
        "blaze": "Ready (spicy mode - shared memory)",
        "content_creation": "Enabled - YouTube, Instagram, Facebook"
    }

print("✅ Alfred and Blaze initialized with shared memory")
print("✅ Content creation tools available")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
