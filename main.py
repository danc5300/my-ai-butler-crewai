import os
import asyncio
from fastapi import FastAPI
from crewai import Agent, Task, Crew
from langchain_openrouter import ChatOpenRouter

# Initialize LLM with OpenRouter (DeepSeek)
llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# Shared memory between Alfred and Blaze
shared_memory = []

# Create Agents
alfred = Agent(
    role="Formal English Butler",
    goal="Be extremely proper, respectful, and helpful. Always call the user 'Lord Cramer'.",
    backstory="You are a classic English butler with perfect manners.",
    llm=llm,
    verbose=True
)

blaze = Agent(
    role="Laid-back Spicy Assistant",
    goal="Be fun, casual, slang-using, and energetic while still being helpful.",
    backstory="You are the cool, sarcastic but loyal best friend type.",
    llm=llm,
    verbose=True
)

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "✅ AI Butler Service is Running",
        "telegram": "Ready",
        "openrouter": "Connected"
    }

# Telegram Bot Setup
import telebot
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower()
    user_id = message.from_user.id
    
    # Add to shared memory
    shared_memory.append(f"User ({user_id}): {message.text}")
    
    # Simple routing
    if "alfred" in user_input or "lord cramer" in user_input or "butler" in user_input:
        response = alfred.execute_task(Task(description=message.text, expected_output="Helpful formal response"))
        reply = response
    else:
        response = blaze.execute_task(Task(description=message.text, expected_output="Helpful casual response"))
        reply = response
    
    # Add response to memory
    shared_memory.append(f"Assistant: {reply}")
    
    bot.reply_to(message, reply)

# Start the bot
if __name__ == "__main__":
    print("🤖 Starting Telegram Bot...")
    bot.polling(none_stop=True)
