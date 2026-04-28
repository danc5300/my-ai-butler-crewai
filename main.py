import discord
import os

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now ONLINE!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if "@alfred" in message.content.lower() or "alfred" in message.content.lower():
        await message.reply("Very good, Lord Cramer. How may I assist you today, sir?")
    elif "@blaze" in message.content.lower() or "blaze" in message.content.lower():
        await message.reply("Yo what's good? 🔥 Let's get this shit done.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
