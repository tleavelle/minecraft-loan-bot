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

    # If LOG_CHANNEL_ID is set, send it as a Discord message
    if LOG_CHANNEL_ID:
        try:
            channel = bot.get_channel(LOG_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"📜 {action}",
                    description=f"**User:** {user.mention}\n**Details:** {details}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.set_footer(text=f"Action: {action}")
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to log to Discord channel: {e}")

