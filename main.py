import os
import telebot
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

# Initialize LLM
llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip()
    
    # Simple prompt for Alfred or Blaze
    if any(word in user_text.lower() for word in ["alfred", "lord cramer", "butler", "formal"]):
        system_prompt = "You are Alfred, a very formal, proper English butler. Always call the user 'Lord Cramer'. Be respectful and efficient."
    else:
        system_prompt = "You are Blaze, a cool, laid-back, slightly spicy and fun assistant. Use casual slang and keep it energetic."
    
    try:
        response = llm.invoke([
            HumanMessage(content=f"{system_prompt}\n\nUser: {user_text}")
        ])
        bot.reply_to(message, response.content)
    except Exception as e:
        bot.reply_to(message, "Sorry, I'm having a small issue right now. Please try again.")

if __name__ == "__main__":
    print("🤖 Telegram AI Butler Bot is now running...")
    bot.polling(none_stop=True)
