import os
import json
import telebot
from datetime import datetime
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=OPENROUTER_KEY
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ====================== MEMORY SYSTEM ======================
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
                         "• Just chat normally for Blaze (casual & fun)")

# ====================== MAIN HANDLER ======================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Initialize user memory
    if user_id not in memory:
        memory[user_id] = {"name": message.from_user.first_name or "Cramer", "preferences": {}, "history": []}
    
    user_memory = memory[user_id]

    # Determine mode
    if any(word in text.lower() for word in ["alfred", "butler", "lord cramer", "formal", "sir"]):
        system = f"""You are Alfred, a highly professional English butler.
Current date: {current_date}
User's name: Lord {user_memory['name']}
You have permanent memory of this user. Be formal, respectful, and anticipatory."""
    else:
        system = f"""You are Blaze, a cool, laid-back, fun and slightly spicy assistant.
Current date: {current_date}
User's name: {user_memory['name']}
You have permanent memory of this user. Be casual, energetic, and use some slang."""

    try:
        response = llm.invoke([
            HumanMessage(content=f"{system}\n\nUser: {text}")
        ])
        
        bot.reply_to(message, response.content)
        
        # Save to memory
        user_memory["history"].append({"date": current_date, "user": text, "assistant": response.content})
        if len(user_memory["history"]) > 50:  # Keep last 50 exchanges
            user_memory["history"] = user_memory["history"][-50:]
        save_memory(memory)

    except Exception as e:
        bot.reply_to(message, "Sorry Lord Cramer, I'm having a small issue. Please try again.")

if __name__ == "__main__":
    print("✅ Alfred & Blaze with Persistent Memory Started")
    bot.infinity_polling()
