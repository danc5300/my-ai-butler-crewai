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

# ====================== HEALTH CHECK ======================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ Alfred & Blaze are online!\n\nMention 'Alfred' for formal help, or just chat normally for Blaze.")

@app.get("/")  # For Render health check
async def health():
    return {"status": "running", "bot": "Alfred & Blaze"}

# ====================== MAIN HANDLER ======================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        text = message.text.strip()
        user_name = message.from_user.first_name or "User"

        if any(x in text.lower() for x in ["alfred", "butler", "lord cramer", "formal"]):
            system = f"You are Alfred, a proper English butler. Address the user as 'Lord {user_name}' or 'Lord Cramer'. Be formal and helpful."
        else:
            system = f"You are Blaze, a cool, casual, slightly spicy assistant. Be fun and energetic with {user_name}."

        response = llm.invoke([
            HumanMessage(content=f"{system}\n\nUser: {text}")
        ])

        bot.reply_to(message, response.content)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I'm having a moment. Try again!")

# ====================== START BOT ======================
if __name__ == "__main__":
    print("🚀 Starting Alfred & Blaze Telegram Bot...")
    print("✅ Bot is ready. Send /start to test.")
    
    # Run with longer timeout to reduce conflicts
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
