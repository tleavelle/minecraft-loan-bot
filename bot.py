# bot.py

import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from db import initialize_db
from commands import setup_commands

# Setup the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    initialize_db()

# Register commands
setup_commands(bot)

# Run the bot
bot.run(DISCORD_TOKEN)
