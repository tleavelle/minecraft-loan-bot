# logger.py

import os
import discord
from datetime import datetime
from config import LOG_CHANNEL_ID

LOG_FILE_PATH = "logs/loanbot.log"

# Ensure the logs folder exists
os.makedirs("logs", exist_ok=True)

async def log_transaction(bot, action: str, user: discord.User, details: str):
    """Logs a transaction to a file and optionally to a Discord channel."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_tag = f"{user.name}#{user.discriminator}"
    log_entry = f"[{timestamp}] {action} | {user_tag} | {details}\n"

    # Write to local log file
    with open(LOG_FILE_PATH, "a") as f:
        f.write(log_entry)

    # Also send to Discord log channel, if configured
    if LOG_CHANNEL_ID:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=f"📜 {action}",
                description=f"**User:** {user.mention}\n**Details:** {details}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send log to Discord: {e}")
