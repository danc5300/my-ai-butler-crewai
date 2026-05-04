import os
from datetime import datetime
import telebot
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=OPENROUTER_KEY
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "✅ **Alfred & Blaze are online!**\n\n"
                         "• Say 'Alfred' for formal butler mode\n"
                         "• Just chat normally for Blaze (casual & fun)")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        text = message.text.strip()
        user_name = message.from_user.first_name or "Cramer"
        current_date = datetime.now().strftime("%B %d, %Y")

        if any(word in text.lower() for word in ["alfred", "butler", "lord cramer", "formal", "sir"]):
            system = f"""You are Alfred, a highly professional English butler. 
Current date is {current_date}.
Always address the user as 'Lord Cramer' or 'Lord {user_name}'.
Be formal, respectful, and precise. If you don't know real-time information, say so honestly."""
        else:
            system = f"""You are Blaze, a cool, laid-back, fun and slightly spicy assistant.
Current date is {current_date}.
Use casual language, slang, and energy. Be helpful and fun."""

        response = llm.invoke([
            HumanMessage(content=f"{system}\n\nUser: {text}")
        ])

        bot.reply_to(message, response.content)

    except Exception as e:
        bot.reply_to(message, "Sorry, I'm having a small issue. Please try again.")

if __name__ == "__main__":
    print("✅ Alfred & Blaze Telegram Bot is running...")
    bot.infinity_polling()
