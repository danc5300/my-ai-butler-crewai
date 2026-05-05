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

# Usage Limits
LIMITS = {"free": 15, "essential": 100, "premium": 500}

LAST_BRIEF_DATE = {}

# Morning Brief Templates (for variety)
MORNING_TEMPLATES = [
    "Good morning {name}! Let's crush this day.",
    "Rise and shine, {name}! Here's your morning fuel.",
    "Yo {name}! New day, new energy — here's the brief.",
    "Morning, {name}! Time to own the day.",
    "Hey {name}, hope you're feeling unstoppable today!"
]

def send_morning_brief(user_id):
    if user_id not in memory:
        return
    user = memory[user_id]
    name = user.get("name", "friend")

    try:
        weather = search.run("Kalamazoo Michigan weather today")
        hormuz = search.run("Strait of Hormuz ship traffic last 24 hours")
        
        template = random.choice(MORNING_TEMPLATES)
        prompt = f"""You are Blaze, energetic and casual.
Current time: {datetime.now().strftime("%B %d, %Y at %I:%M %p EST")}

{template.format(name=name)}

Weather in Kalamazoo: {weather}
Strait of Hormuz last 24h: {hormuz}

Create a fun, positive morning briefing. Always include:
- Short Kalamazoo weather
- Latest ship count + short context why low
- One inspirational Bible verse

Keep it warm and personal."""

        response = llm.invoke(prompt)
        bot.send_message(user_id, response.content)
    except:
        bot.send_message(user_id, f"Morning {name}! Have a great day!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())
    now = datetime.now()

    # New user welcome
    if user_id not in memory:
        memory[user_id] = {
            "name": "friend",
            "tier": "free",
            "usage": {}
        }
        bot.reply_to(message, "Welcome to My AI Butler! 🎉 I'm here with Alfred (formal) and Blaze (fun). Try messaging me anytime. Type /help for commands.")
    
    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    # Commands
    if text == "/help":
        bot.reply_to(message, "Commands:\n/upgrade - Upgrade your plan\n/cancel - Cancel subscription\n/help - Show this menu")
        return
    if text == "/upgrade":
        bot.reply_to(message, "🔼 Upgrade your plan here:\n• Essential ($29/mo): [Polar Essential Link]\n• Premium ($49/mo): [Polar Premium Link]\nJust reply with the plan you want!")
        return
    if text.startswith("/cancel"):
        bot.reply_to(message, "⚠️ Are you sure you want to cancel? Reply **YES** to confirm (this will stop morning briefs and access).")
        return
    if text == "YES" and "cancel" in memory.get(user_id, {}).get("last_message", ""):
        bot.reply_to(message, "Subscription cancelled. Sorry to see you go — you can rejoin anytime!")
        # Add Polar cancel link later
        return

    # Auto morning brief after 8 AM
    if now.hour >= 8 and LAST_BRIEF_DATE.get(user_id) != today:
        send_morning_brief(user_id)
        LAST_BRIEF_DATE[user_id] = today

    # Usage check
    if daily_count >= limit:
        bot.reply_to(message, f"Sorry {user.get('name', 'there')}, you've reached your daily limit of {limit} messages on the {tier} plan.\n\n🔼 Want more? Type /upgrade to get higher limits!")
        return

    # Personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal English butler. Address the user as 'Lord Cramer'."
    else:
        personality = "You are Blaze, energetic, casual and fun."

    current_time = now.strftime("%B %d, %Y at %I:%M %p EST")

    try:
        response = llm.invoke(f"{personality}\nCurrent time: {current_time}\nUser: {text}")
        bot.reply_to(message, response.content)

        user["usage"][today] = daily_count + 1
        user["last_message"] = text
        save_memory(memory)
    except:
        bot.reply_to(message, "Small glitch — try again shortly.")

print("🤖 Alfred & Blaze running...")
bot.infinity_polling()
