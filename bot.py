import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from config import DISCORD_TOKEN, ALLOWED_CHANNELS, GUILD_ID
from db import initialize_db
from commands import setup_commands
from loans import get_overdue_loans
from logger import log_transaction

# Create folders
os.makedirs("Loan Agreements", exist_ok=True)
os.makedirs("logs", exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    initialize_db()
    try:
        guild = discord.Object(id=GUILD_ID)
        await tree.clear_commands(guild=guild)
        setup_commands(bot)
        synced = await tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
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
            embed = discord.Embed(title="📅 Overdue Loans", color=discord.Color.orange())
            for loan_id, player_name, due in overdue_loans:
                embed.add_field(name=f"Loan #{loan_id}", value=f"{player_name} due {due}", inline=False)
            await channel.send(embed=embed)
    for loan_id, player_name, due in overdue_loans:
        await log_transaction(bot, "Overdue Check", bot.user, f"Loan #{loan_id} overdue for {player_name} (due {due})")

@daily_overdue_check.before_loop
async def before_daily_check():
    import asyncio
    from datetime import datetime, timedelta
    now = datetime.now()
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())

try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    print(f"❌ Bot failed to start: {e}")
