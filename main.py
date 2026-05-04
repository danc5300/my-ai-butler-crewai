import os
import json
import telebot
from datetime import datetime
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=OPENROUTER_KEY
)

search = DuckDuckGoSearchRun()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ====================== MEMORY ======================
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
        json.dump(memory, f, indent=2)

memory = load_memory()

# ====================== COMMANDS ======================
@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    user_id = str(message.from_user.id)
    if user_id not in memory:
        memory[user_id] = {"name": message.from_user.first_name or "Cramer", "preferences": {}, "history": []}
        save_memory(memory)
    
    bot.reply_to(message, f"✅ **Alfred & Blaze are online, Lord {memory[user_id]['name']}!**\n\n"
                         "• Say 'Alfred' for formal butler mode\n"
                         "• Just chat normally for Blaze")

# ====================== MAIN HANDLER ======================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    if user_id not in memory:
        memory[user_id] = {"name": message.from_user.first_name or "Cramer", "preferences": {}, "history": []}
    
    user_memory = memory[user_id]

    # Decide mode
    if any(word in text.lower() for word in ["alfred", "butler", "lord cramer", "formal", "sir"]):
        personality = f"You are Alfred, a highly professional English butler. Current date: {current_date}. Address user as 'Lord {user_memory['name']}'."
    else:
        personality = f"You are Blaze, a cool, laid-back, fun assistant. Current date: {current_date}. Use casual energy."

    try:
        # Use search if question looks factual / current
        if any(word in text.lower() for word in ["current", "today", "latest", "now", "how many", "what is", "news", "update", "hormuz", "weather", "stock"]):
            search_result = search.run(text[:200])  # Limit query length
            full_prompt = f"{personality}\n\nRecent search results: {search_result}\n\nUser question: {text}"
        else:
            full_prompt = f"{personality}\n\nUser: {text}"

        response = llm.invoke([HumanMessage(content=full_prompt)])
        
        bot.reply_to(message, response.content)
        
        # Save conversation to memory
        user_memory["history"].append({"date": current_date, "user": text, "assistant": response.content})
        if len(user_memory["history"]) > 50:
            user_memory["history"] = user_memory["history"][-50:]
        save_memory(memory)

    except Exception as e:
        bot.reply_to(message, "Sorry, I'm having a small technical issue right now. Please try again.")

if __name__ == "__main__":
    print("✅ Alfred & Blaze with Memory + Real-time Search Started")
    bot.infinity_polling()
