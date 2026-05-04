import os
import json
import telebot
from datetime import datetime, date
from langchain_openrouter import ChatOpenRouter
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize LLM and tools
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
    "premium": 500
}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    lower = text.lower()
    today = str(date.today())

    # Initialize user with your family details
    if user_id not in memory:
        memory[user_id] = {
            "name": "Dan Cramer",
            "wife": "Tara",
            "children": "three boys",
            "dog": "Atlas (half German Shepherd, half Great Pyrenees)",
            "tier": "free",          # Change to "essential" or "premium" for testing
            "usage": {}
        }

    user = memory[user_id]
    tier = user.get("tier", "free")
    daily_count = user["usage"].get(today, 0)
    limit = LIMITS.get(tier, 15)

    # Check daily limit
    if daily_count >= limit:
        bot.reply_to(message, f"Sorry {user['name']}, you've reached your daily limit of {limit} messages on the {tier} plan. Come back tomorrow or upgrade!")
        return

    # Determine personality
    if any(word in lower for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a very formal, proper English butler. Always address the user as 'Lord Cramer'. Be respectful, precise, and professional."
        greeting = "Very good, Lord Cramer."
    else:
        personality = "You are Blaze, a cool, energetic, slightly spicy and fun assistant. Use casual slang and keep energy high."
        greeting = "Yo what's good!"

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Real-time search for relevant queries
    if "hormuz" in lower and any(word in lower for word in ["ship", "traffic", "how many", "passed", "latest", "current"]):
        try:
            search_result = search.run("Strait of Hormuz ship traffic last 24 hours")
            full_prompt = f"""{personality}

Current date and time: {current_time}
Family details: Dan Cramer, wife Tara, three boys, dog Atlas (half German Shepherd, half Great Pyrenees)
Latest search results: {search_result}

User asked: {text}

Answer directly with the most recent data and include context on why traffic is low. Be honest about data freshness."""
        except:
            full_prompt = f"{personality}\nCurrent time: {current_time}\nUser: {text}"
    else:
        full_prompt = f"""{personality}

Current date and time: {current_time}
Family details: Dan Cramer, wife Tara, three boys, dog Atlas (half German Shepherd, half Great Pyrenees)
User asked: {text}"""

    try:
        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        
        # Update usage count
        user["usage"][today] = daily_count + 1
        save_memory(memory)
        
    except:
        bot.reply_to(message, f"{greeting} Small technical issue — please try again shortly.")

print("🤖 Alfred & Blaze are running with usage limits and family memory...")
bot.infinity_polling()
