import os
import json
import telebot
from datetime import datetime
from langchain_openrouter import ChatOpenRouter
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize LLM
llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

search = DuckDuckGoSearchRun()

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# Simple persistent memory
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
    
    # Load or init user memory
    if user_id not in memory:
        memory[user_id] = {"name": "Lord Cramer", "preferences": {}}
    
    # Determine personality
    if any(word in text.lower() for word in ["alfred", "lord cramer", "butler", "formal", "sir"]):
        personality = "You are Alfred, a very formal, proper English butler. Always address the user as 'Lord Cramer'. Speak elegantly and respectfully."
        greeting = "Very good, Lord Cramer."
    else:
        personality = "You are Blaze, a cool, energetic, slightly spicy and fun assistant. Use casual slang and keep energy high."
        greeting = "Yo what's good!"

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Real-time search trigger
    search_query = None
    if any(word in text.lower() for word in ["how many", "ships", "hormuz", "strait", "current", "today", "latest", "update", "traffic"]):
        search_query = text

    try:
        if search_query:
            search_result = search.run(search_query)
            full_prompt = f"{personality}\n\nCurrent date and time: {current_time}\nRecent search results: {search_result}\n\nUser asked: {text}\nGive a direct, accurate answer."
        else:
            full_prompt = f"{personality}\n\nCurrent date and time: {current_time}\nUser asked: {text}\nAnswer helpfully and in character."

        response = llm.invoke(full_prompt)
        bot.reply_to(message, response.content)
        
        # Save memory
        memory[user_id]["last_message"] = text
        save_memory(memory)
        
    except Exception as e:
        bot.reply_to(message, f"{greeting} I'm having a small technical issue right now. Please try again.")

print("🤖 Alfred & Blaze Telegram Bot is running...")
bot.infinity_polling()
