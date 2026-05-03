import os
import telebot
import time
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not TELEGRAM_TOKEN or not OPENROUTER_KEY:
    print("❌ Missing environment variables!")
    exit(1)

# Initialize LLM
llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=OPENROUTER_KEY
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

print("🚀 Alfred & Blaze Telegram Bot Starting...")

# ====================== COMMANDS ======================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ **Alfred & Blaze are online!**\n\n"
                         "• Say 'Alfred' for formal butler mode\n"
                         "• Just chat normally for Blaze (casual & fun)")

# ====================== MAIN HANDLER ======================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        text = message.text.strip()
        user_name = message.from_user.first_name or "User"

        if any(word in text.lower() for word in ["alfred", "butler", "lord cramer", "formal", "sir"]):
            system = f"You are Alfred, a very proper English butler. Always address the user as 'Lord {user_name}' or 'Lord Cramer'. Be respectful, elegant and helpful."
        else:
            system = f"You are Blaze, a cool, laid-back, slightly spicy and fun assistant. Use casual language, slang, and be energetic with {user_name}."

        response = llm.invoke([
            HumanMessage(content=f"{system}\n\nUser: {text}")
        ])

        bot.reply_to(message, response.content)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry Lord Cramer, I'm having a small technical issue. Please try again.")

# ====================== START ======================
if __name__ == "__main__":
    print("✅ Bot is now running and listening...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
