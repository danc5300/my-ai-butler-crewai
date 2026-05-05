import os
import json
import telebot
import random
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

LIMITS = {"free": 15, "essential": 100, "premium": 500}
LAST_BRIEF_DATE = {}

MORNING_TEMPLATES = [
    "Good morning {name}! Let's make today awesome.",
    "Rise and shine, {name}! Here's your morning boost.",
    "Yo {name}! New day, fresh energy — let's go!",
    "Morning {name}! Time to crush it.",
    "Hey {name}, hope you're ready — here's the brief!"
]

def send_morning_brief(user_id, personality="Blaze"):
    if user_id not in memory:
        return
    user = memory[user_id]
    name = user.get("name", "friend")

    try:
        weather = search.run("Kalamazoo Michigan current weather and forecast today")
        hormuz = search.run("Strait of Hormuz ship traffic last 24 hours latest")
        
        template = random.choice(MORNING_TEMPLATES)
        prompt = f"""You are {personality}, {'a formal English butler who addresses the user as Lord Cramer' if personality == 'Alfred' else 'energetic, casual and fun'}.
Current exact time: {datetime.now().strftime("%B %d, %Y at %I:%M %p EST")}

{template.format(name=name)}

Weather in Kalamazoo right now: {weather}
Strait of Hormuz last 24 hours: {hormuz}

Create a positive morning briefing. Always include:
- Short accurate Kalamazoo weather
- Latest ship count through Strait of Hormuz + short context why it's low
- One inspirational Bible verse

NEVER invent appointments, schedules, or events. Stick to real data only."""

        response = llm.invoke(prompt)
        bot.send_message(user_id, response.content)
    except:
        bot.send_message(user_id, f"Morning {name}! Hope you have a great day!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())
    now = datetime.now()

    # New user welcome
    if user_id not in memory:
        memory[user_id] = {"name": "friend", "tier": "free", "usage": {}}
        bot.reply_to(message, "Welcome to My AI Butler! 🎉 You can talk to Alfred (formal) or Blaze (fun). Type /help for commands.")
        return

    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    # Commands
    if text == "/help":
        bot.reply_to(message, "Commands:\n/upgrade - Upgrade your plan\n/cancel - Cancel subscription\n/help - This menu")
        return
    if text == "/upgrade":
        bot.reply_to(message, "🔼 Upgrade here:\n• Essential ($29/mo) → [Polar Link]\n• Premium ($49/mo) → [Polar Link]")
        return
    if text.startswith("/cancel"):
        bot.reply_to(message, "⚠️ Are you sure you want to cancel? Reply **YES** to confirm.")
        return
    if text == "YES" and "cancel" in user.get("last_message", ""):
        bot.reply_to(message, "Subscription cancelled. You can rejoin anytime!")
        return

    # Auto morning brief after 8 AM (once per day)
    if now.hour >= 8 and LAST_BRIEF_DATE.get(user_id) != today:
        send_morning_brief(user_id)
        LAST_BRIEF_DATE[user_id] = today

    # Usage check
    if daily_count >= limit:
        bot.reply_to(message, f"You've reached your daily limit ({limit} messages). Type /upgrade to increase it!")
        return

    # Personality routing (strict)
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "Alfred"
        greeting = "Very good, Lord Cramer."
    else:
        personality = "Blaze"
        greeting = "Yo what's good!"

    current_time = now.strftime("%B %d, %Y at %I:%M %p EST")

    try:
        response = llm.invoke(f"You are {personality}. Current time: {current_time}. User: {text}")
        bot.reply_to(message, response.content)

        user["usage"][today] = daily_count + 1
        user["last_message"] = text
        save_memory(memory)
    except:
        bot.reply_to(message, f"{greeting} Small glitch — try again shortly.")

print("🤖 Alfred & Blaze running...")
bot.infinity_polling()
