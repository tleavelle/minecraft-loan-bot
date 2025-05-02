import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from config import DISCORD_TOKEN, ALLOWED_CHANNELS, GUILD_ID
from db import initialize_db
from commands import setup_commands
from loans import get_overdue_loans
from logger import log_transaction

# Ensure necessary folders exist
os.makedirs("Loan Agreements", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Setup the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # used for slash commands

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    initialize_db()

    try:
        guild = discord.Object(id=GUILD_ID)

        # Register fresh commands AFTER login
        setup_commands(bot)

        # Optional: Clear existing commands if needed
        # await tree.clear_commands(guild=guild)

        synced = await tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
        for cmd in synced:
            print(f" - /{cmd.name}")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")

    daily_overdue_check.start()

@tasks.loop(hours=24)
async def daily_overdue_check():
    await bot.wait_until_ready()
    overdue_loans = get_overdue_loans()
    if not overdue_loans:
        return

    for channel_id in ALLOWED_CHANNELS:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="📅 Daily Overdue Loan Check",
                color=discord.Color.orange()
            )
            for loan_id, player_name, due_date in overdue_loans:
                embed.add_field(
                    name=f"Loan #{loan_id}",
                    value=f"Player: `{player_name}`\nDue: {due_date}",
                    inline=False
                )
            await channel.send(embed=embed)

    for loan_id, player_name, due_date in overdue_loans:
        await log_transaction(bot, "Daily Overdue Check", bot.user, f"Loan #{loan_id} overdue for {player_name} (due {due_date})")

@daily_overdue_check.before_loop
async def before_daily_check():
    from datetime import datetime, timedelta
    import asyncio
    now = datetime.now()
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())

try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    print(f"❌ Bot failed to start: {e}")
