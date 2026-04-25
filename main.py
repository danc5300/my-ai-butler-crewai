from fastapi import FastAPI, Query
import os
import json
import discord
from discord.ext import commands
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage
import asyncio

app = FastAPI(title="My AI Butler")

# ====================== LLM ======================
llm = ChatOpenRouter(
    model=os.getenv("MODEL", "deepseek/deepseek-chat"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

# ====================== Discord Bot ======================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("@Alfred") or "alfred" in message.content.lower():
        response = await get_alfred_response(message.content)
        await message.reply(response)

    elif message.content.startswith("@Blaze") or "blaze" in message.content.lower():
        response = await get_blaze_response(message.content)
        await message.reply(response)

async def get_alfred_response(user_message):
    try:
        prompt = f"You are Alfred, formal English butler. Speak cleanly and professionally. Address as 'Lord Cramer' or 'Sir'.\nUser: {user_message}\nAlfred:"
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response
    except:
        return "Very good, Lord Cramer. How may I assist you today, sir?"

async def get_blaze_response(user_message):
    try:
        prompt = f"You are Blaze, spicy and fun. Speak casually with energy.\nUser: {user_message}\nBlaze:"
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response
    except:
        return "Yo what's good? 🔥 Let's get this shit done."

# ====================== FastAPI ======================
@app.get("/")
def root():
    return {"status": "✅ My AI Butler is running with Discord"}

# Start Discord bot in background
@app.on_event("startup")
async def startup():
    asyncio.create_task(bot.start(os.getenv("DISCORD_BOT_TOKEN")))

print("✅ Server starting with Discord bot")
