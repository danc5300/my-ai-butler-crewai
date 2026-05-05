import os
import json
import telebot
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

LAST_BRIEF_DATE = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())
    now = datetime.now()

    # Initialize user
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
        bot.reply_to(message, f"Sorry {user['name']}, you've reached your daily limit of {limit} messages.")
        return

    # === AUTO MORNING BRIEF (after 8:00 AM EST) ===
    if now.hour >= 8 and LAST_BRIEF_DATE.get(user_id) != today:
        send_morning_brief(user_id)
        LAST_BRIEF_DATE[user_id] = today

    # Normal response
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal English butler. Address the user as 'Lord Cramer'."
    else:
        personality = "You are Blaze, energetic, casual and fun."

    current_time = now.strftime("%B %d, %Y at %I:%M %p EST")

    try:
        response = llm.invoke(f"{personality}\nCurrent time: {current_time}\nUser: {text}")
        bot.reply_to(message, response.content)

        user["usage"][today] = daily_count + 1
        save_memory(memory)
    except:
        bot.reply_to(message, "Small glitch — try again shortly.")

def send_morning_brief(user_id):
    """Send the 8 AM morning brief"""
    try:
        weather = search.run("Kalamazoo Michigan weather today")
        hormuz = search.run("Strait of Hormuz ship traffic last 24 hours")
        
        prompt = f"""You are Blaze, a cool, energetic, slightly spicy assistant.
Current time: {datetime.now().strftime("%B %d, %Y at %I:%M %p EST")}

Family: Dan Cramer, wife Tara, three boys, dog Atlas (half German Shepherd, half Great Pyrenees)

Weather in Kalamazoo: {weather}
Strait of Hormuz last 24 hours: {hormuz}

Create a fun, positive morning briefing. Always include:
- Short Kalamazoo weather report
- Latest ship count through Strait of Hormuz + short context why it's low
- One inspirational Bible verse

Keep energy high and personal."""

        response = llm.invoke(prompt)
        bot.send_message(user_id, response.content)
    except:
        bot.send_message(user_id, "Yo Dan! Quick morning check-in — have an awesome day!")

print("🤖 Alfred & Blaze running with auto morning briefs...")
bot.infinity_polling()
