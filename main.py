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
    lower_text = text.lower()
    
    if user_id not in memory:
        memory[user_id] = {"name": "Lord Cramer"}

    # Personality
    if any(word in lower_text for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a formal and proper English butler. Address the user exclusively as 'Lord Cramer'. Be precise, professional, and honest about data limitations."
    else:
        personality = "You are Blaze, a cool, energetic, and slightly spicy assistant. Use casual, fun language."

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Force fresh search on Hormuz queries
    if "hormuz" in lower_text and ("ship" in lower_text or "traffic" in lower_text or "how many" in lower_text):
        try:
            # More specific and recent-focused query
            search_result = search.run("Strait of Hormuz number of ships last 24 hours site:reuters.com OR site:bbc.com OR site:marinetraffic.com OR site:lloydslist.com")
            full_prompt = f"""{personality}

Current date and time: {current_time}
Latest search results: {search_result}

User asked: {text}

Answer directly with the most recent reliable figure. If data is unclear or conflicting, say so honestly. Do not guess or use old numbers."""
        except:
            full_prompt = f"{personality}\nCurrent time: {current_time}\nI couldn't fetch live data right now."
    else:
        full_prompt = f"{personality}\nCurrent time: {current_time}\nUser: {text}"

    try:
        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        memory[user_id]["last_message"] = text
        save_memory(memory)
    except:
        bot.reply_to(message, "Small technical issue — please try again shortly.")

print("🤖 Alfred & Blaze running...")
bot.infinity_polling()
