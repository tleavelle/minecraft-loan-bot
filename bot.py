# bot.py

import os
import discord
from discord import Bot  # ✅ use the correct class for slash commands
from config import DISCORD_TOKEN
from db import initialize_db
from commands import setup_commands

# Ensure necessary folders exist
os.makedirs("Loan Agreements", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Setup the bot with slash command support
intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)  # ✅ replaces commands.Bot

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    initialize_db()

# Register slash commands
setup_commands(bot)

# Run the bot
try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    print(f"Failed to start bot: {e}")
