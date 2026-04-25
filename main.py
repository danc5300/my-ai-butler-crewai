import discord
import os
import asyncio
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage

# ====================== LLM ======================
llm = ChatOpenRouter(
    model=os.getenv("MODEL", "deepseek/deepseek-chat"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# ====================== Discord Bot ======================
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is ONLINE and connected!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if "@alfred" in content or "alfred" in content:
        try:
            prompt = f"You are Alfred, a formal English-style butler. Speak cleanly and professionally. Address as 'Lord Cramer' or 'Sir'.\nUser: {message.content}\nAlfred:"
            response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
            await message.reply(response)
        except:
            await message.reply("Very good, Lord Cramer. How may I assist you today, sir?")

    elif "@blaze" in content or "blaze" in content:
        try:
            prompt = f"You are Blaze, spicy, casual and fun. Speak naturally.\nUser: {message.content}\nBlaze:"
            response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
            await message.reply(response)
        except:
            await message.reply("Yo what's good? 🔥 Let's get this shit done.")

# ====================== Start Bot ======================
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
