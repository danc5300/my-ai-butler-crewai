import os
import json
import telebot
import schedule
import time
import threading
from datetime import datetime, date
from langchain_openrouter import ChatOpenRouter
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize
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
LIMITS = {"free": 15, "essential": 100, "premium": 500}

def send_morning_brief():
    """Automatic 8 AM EST morning update"""
    user_id = "7663595375"   # Your Telegram ID
    if user_id not in memory:
        return
    
    user = memory[user_id]
    name = user.get("name", "Dan")

    try:
        weather = search.run("Kalamazoo Michigan weather today")
        hormuz = search.run("Strait of Hormuz ship traffic last 24 hours")
        
        prompt = f"""You are Blaze, a cool, energetic, slightly spicy assistant.
Current date and time: {datetime.now().strftime("%B %d, %Y at %I:%M %p EST")}

User: {name}
Family: Wife Tara, three boys, dog Atlas (half German Shepherd, half Great Pyrenees)

Weather in Kalamazoo: {weather}
Strait of Hormuz last 24 hours: {hormuz}

Create a fun, positive morning briefing. Always include:
- Short weather report for Kalamazoo
- Latest ship count through Strait of Hormuz + short context why it's low
- One inspirational Bible verse
Keep the energy high and casual. Make it feel personal."""

        response = llm.invoke(prompt)
        bot.send_message(user_id, response.content)
        
    except:
        bot.send_message(user_id, f"Yo {name}! Quick morning check-in — everything's good, have an awesome day!")

# Schedule 8 AM EST daily
def run_scheduler():
    schedule.every().day.at("08:00").do(send_morning_brief)
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

# Normal message handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())

    if user_id not in memory:
        memory[user_id] = {
            "name": "Dan Cramer",
            "wife": "Tara",
            "children": "three boys",
            "dog": "Atlas (half German Shepherd, half Great Pyrenees)",
            "tier": "free",
            "usage": {}
        }

    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    if daily_count >= limit:
        bot.reply_to(message, f"Sorry {user['name']}, you've hit your daily limit ({limit} messages). Come back tomorrow or upgrade!")
        return

    # Personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal English butler. Address user as 'Lord Cramer'."
        greeting = "Very good, Lord Cramer."
    else:
        personality = "You are Blaze, energetic and casual."
        greeting = "Yo what's good!"

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    try:
        response = llm.invoke(f"{personality}\nCurrent time: {current_time}\nUser: {text}")
        bot.reply_to(message, response.content)

        user["usage"][today] = daily_count + 1
        save_memory(memory)
    except:
        bot.reply_to(message, f"{greeting} Small glitch — try again!")

print("🤖 Alfred & Blaze running with 8 AM morning briefs...")
bot.infinity_polling()
