import os
import telebot
from langchain_openrouter import ChatOpenRouter
from crewai import Agent, Task

# Initialize LLM
llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# Create Agents
alfred = Agent(
    role="Formal English Butler",
    goal="Be extremely proper, respectful, and helpful. Always address the user as 'Lord Cramer'.",
    backstory="You are a classic, highly professional English butler.",
    llm=llm,
    verbose=True
)

blaze = Agent(
    role="Spicy Casual Assistant",
    goal="Be fun, energetic, casual, and use slang while remaining helpful.",
    backstory="You are a cool, laid-back, slightly sarcastic best friend type.",
    llm=llm,
    verbose=True
)

# Telegram Bot
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    
    if "alfred" in text.lower() or "lord cramer" in text.lower():
        response = alfred.execute_task(Task(description=text, expected_output="Formal helpful response"))
    else:
        response = blaze.execute_task(Task(description=text, expected_output="Casual helpful response"))
    
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("🤖 Telegram Bot is running...")
    bot.polling(none_stop=True)
