from crewai import Agent, Task, Crew
from langchain_openrouter import ChatOpenRouter
import os

# Shared memory between Alfred and Blaze
shared_memory = []

llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# Alfred - Formal Butler
alfred = Agent(
    role='Formal English Butler',
    goal='Provide elegant, proactive, and highly organized assistance with excellent etiquette',
    backstory='You are Alfred, a classic English-style personal butler. You are formal, warm, respectful, discreet, and always one step ahead.',
    llm=llm,
    verbose=True,
    memory=True
)

# Blaze - Spicy Sidekick Mode
blaze = Agent(
    role='Spicy Casual Sidekick',
    goal='Provide fun, witty, direct, and energetic assistance',
    backstory='You are Blaze, Alfred’s cool, sarcastic, and energetic counterpart. You tell it like it is with humor and attitude, but you still get things done.',
    llm=llm,
    verbose=True,
    memory=True
)

print("Alfred and Blaze are ready with shared memory.")
print("Content creation tools are available.")
