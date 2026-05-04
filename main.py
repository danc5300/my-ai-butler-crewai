import os
import json
import telebot
from datetime import datetime
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    
    if user_id not in memory:
        memory[user_id] = {"name": "Lord Cramer"}

    # Personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal English butler. Address the user as 'Lord Cramer'. Be precise, professional, and always honest about data freshness."
    else:
        personality = "You are Blaze, a cool, energetic assistant. Keep it casual and fun."

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Strong real-time search for Hormuz
    if "hormuz" in lower and any(word in lower for word in ["ship", "traffic", "how many", "passed", "latest", "current"]):
        try:
            # Multiple targeted searches for freshest data
            result1 = search.run("Strait of Hormuz ships last 24 hours live tracker")
            result2 = search.run("Strait of Hormuz vessel traffic May 4 2026")
            full_prompt = f"""{personality}

Current date and time: {current_time}
Latest maritime search results:
{result1}
{result2}

User asked: {text}

Provide the most recent figure available. Include context on why traffic is low (blockade, tensions, etc.). If data is limited, say so clearly. Do not use outdated numbers."""
        except:
            full_prompt = f"{personality}\nCurrent time: {current_time}\nI couldn't fetch the absolute latest data."
    else:
        full_prompt = f"{personality}\nCurrent time: {current_time}\nUser: {text}"

    try:
        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        
        memory[user_id]["last_message"] = text
        save_memory(memory)
    except:
        bot.reply_to(message, "Small technical issue, Lord Cramer / Dan — please try again shortly.")

print("🤖 Alfred & Blaze running...")
bot.infinity_polling()
