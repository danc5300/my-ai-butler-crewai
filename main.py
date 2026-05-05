import os
import json
import telebot
import random
from datetime import datetime, date
from zoneinfo import ZoneInfo
from langchain_openrouter import ChatOpenRouter
from langchain_community.tools import DuckDuckGoSearchRun

llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

search = DuckDuckGoSearchRun()
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

MEMORY_FILE = "user_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

LIMITS = {"free": 15, "essential": 100, "premium": 500}
LAST_BRIEF_DATE = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())

    # New user welcome (only once)
    if user_id not in memory:
        memory[user_id] = {"name": "friend", "tier": "free", "usage": {}}
        bot.reply_to(message, "Welcome to My AI Butler! 🎉 Talk to Alfred (formal) or Blaze (fun). Type /help for commands.")
        save_memory(memory)
        return

    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    # Immediate acknowledgement
    bot.reply_to(message, "Got it! Working on that right now...")

    # Usage check
    if daily_count >= limit:
        bot.reply_to(message, f"You've reached your daily limit ({limit} messages). Type /upgrade to get more!")
        return

    # Personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "Alfred"
    else:
        personality = "Blaze"

    # Force Eastern Time for Kalamazoo
    eastern = ZoneInfo("America/New_York")
    current_time = datetime.now(eastern).strftime("%B %d, %Y at %I:%M %p EST")

    try:
        full_prompt = f"You are {personality}. Current exact time in Kalamazoo, Michigan: {current_time}. User: {text}. Be accurate and factual."

        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)

        user["usage"][today] = daily_count + 1
        save_memory(memory)
    except:
        bot.reply_to(message, "Small glitch — try again shortly.")

print("🤖 Alfred & Blaze running...")
bot.infinity_polling()
