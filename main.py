import os
import json
import telebot
from datetime import datetime, date
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

# Usage Limits
LIMITS = {
    "free": 15,
    "essential": 100,
    "premium": 500   # practically unlimited for now
}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())

    # Initialize user
    if user_id not in memory:
        memory[user_id] = {
            "name": "Lord Cramer",
            "tier": "free",           # Change to "essential" or "premium" manually for testing
            "usage": {}
        }
    
    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    # Check limit
    if daily_count >= limit:
        bot.reply_to(message, f"I'm sorry {user['name']}, you've reached your daily limit of {limit} messages on the {tier} plan. Come back tomorrow or upgrade for more usage!")
        return

    # Personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal English butler. Address the user as 'Lord Cramer'. Be precise and professional."
        greeting = "Very good, Lord Cramer."
    else:
        personality = "You are Blaze, a cool, energetic assistant. Keep it casual and fun."
        greeting = "Yo what's good!"

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Search trigger
    if "hormuz" in lower and any(word in lower for word in ["ship", "traffic", "how many", "passed", "latest"]):
        try:
            search_result = search.run("Strait of Hormuz ship traffic last 24 hours")
            full_prompt = f"""{personality}

Current time: {current_time}
Search results: {search_result}

User: {text}

Answer directly with the latest data and context."""
        except:
            full_prompt = f"{personality}\nCurrent time: {current_time}\nUser: {text}"
    else:
        full_prompt = f"{personality}\nCurrent time: {current_time}\nUser: {text}"

    try:
        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        
        # Update usage
        user["usage"][today] = daily_count + 1
        save_memory(memory)
        
    except:
        bot.reply_to(message, f"{greeting} Small issue — try again shortly.")

print("🤖 Alfred & Blaze running with usage limits...")
bot.infinity_polling()
