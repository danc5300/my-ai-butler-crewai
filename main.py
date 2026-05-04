import os
import json
import telebot
from datetime import datetime
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip().lower()
    
    if user_id not in memory:
        memory[user_id] = {"name": "Lord Cramer", "preferences": {}}
    
    # Personality
    if any(word in text for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a very formal, proper English butler. Always address the user as 'Lord Cramer'. Be respectful, precise, and professional. Never guess numbers — say 'according to latest reports' and be honest about uncertainty."
        greeting = "Very good, Lord Cramer."
    else:
        personality = "You are Blaze, a cool, energetic, slightly spicy assistant. Use casual language and keep it fun."
        greeting = "Yo what's good!"

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Force search on relevant queries
    if any(word in text for word in ["ship", "ships", "hormuz", "strait", "traffic", "how many", "latest", "current", "today", "update"]):
        try:
            search_result = search.run("Strait of Hormuz ship traffic last 24 hours")
            full_prompt = f"""{personality}

Current date and time: {current_time}
Recent reliable search results: {search_result}

User asked: {message.text}

Give a direct, accurate answer. Use the most recent data. If numbers vary, pick the latest reliable figure and note the source/date. Do not hallucinate."""
        except:
            full_prompt = f"{personality}\n\nCurrent time: {current_time}\nUser: {message.text}\nI could not fetch live data. Be honest and polite."
    else:
        full_prompt = f"{personality}\n\nCurrent time: {current_time}\nUser: {message.text}"

    try:
        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        
        memory[user_id]["last_message"] = message.text
        save_memory(memory)
    except Exception as e:
        bot.reply_to(message, f"{greeting} Small technical hiccup — try again shortly.")

print("🤖 Alfred & Blaze are online...")
bot.infinity_polling()
