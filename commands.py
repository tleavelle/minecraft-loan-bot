import discord
from discord.ext import commands
from discord import app_commands
from config import OWNER_ID, ALLOWED_CHANNELS, GUILD_ID
from igns import load_igns
from users import link_user, unlink_user, get_user_ign
from loans import apply_for_loan, repay_loan, get_loan_status, get_overdue_loans, get_loan_details_by_id
from logger import log_transaction
from datetime import datetime

igns_set = set(load_igns())

def channel_guard(interaction: discord.Interaction) -> bool:
    return interaction.channel_id in ALLOWED_CHANNELS

def setup_commands(bot: commands.Bot):
    tree = bot.tree

    @tree.command(name="linkuser", description="Link a Discord user to a Minecraft IGN (Admin Only)", guild=discord.Object(id=GUILD_ID))
    async def linkuser(interaction: discord.Interaction, user: discord.Member, ign: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("🚫 You don’t have permission to use this command.", ephemeral=True)
            return
        if not channel_guard(interaction):
            await interaction.response.send_message("🚫 You can't use that command here.", ephemeral=True)
            return
        result = link_user(user.id, ign.strip())
        await interaction.response.send_message(result, ephemeral=True)

    @tree.command(name="unlinkuser", description="Unlink a Discord user from their IGN (Admin Only)", guild=discord.Object(id=GUILD_ID))
    async def unlinkuser(interaction: discord.Interaction, user: discord.Member):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("🚫 You don’t have permission to use this command.", ephemeral=True)
            return
        result = unlink_user(user.id)
        await interaction.response.send_message(result, ephemeral=True)

    @tree.command(name="apply", description="Apply for a diamond loan", guild=discord.Object(id=GUILD_ID))
    async def apply(interaction: discord.Interaction, amount: int):
        if not channel_guard(interaction):
            await interaction.response.send_message("🚫 You can’t use that command here.", ephemeral=True)
            return
        mc_ign = get_user_ign(interaction.user.id)
        if not mc_ign:
            await interaction.response.send_message("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return
        loan_id, summary, agreement_path, due_date = apply_for_loan(mc_ign, amount)
        if loan_id is None:
            await interaction.response.send_message(summary, ephemeral=True)
            return
        embed = discord.Embed(
            title="✅ Loan Approved!",
            description=f"**Loan ID:** `{loan_id}`\n{summary}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed)
        await log_transaction(bot, "Loan Applied", interaction.user, f"{mc_ign} borrowed {amount} diamonds. Due {due_date}.")
        if agreement_path:
            try:
                await interaction.user.send("📄 Here's your loan agreement:", file=discord.File(agreement_path))
            except discord.Forbidden:
                await interaction.followup.send("⚠️ Could not send loan agreement via DM.", ephemeral=True)

    @tree.command(name="repay", description="Repay a loan", guild=discord.Object(id=GUILD_ID))
    async def repay(interaction: discord.Interaction, loan_id: int, amount: float):
        if not channel_guard(interaction):
            await interaction.response.send_message("🚫 You can’t use that command here.", ephemeral=True)
            return
        mc_ign = get_user_ign(interaction.user.id)
        if not mc_ign:
            await interaction.response.send_message("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return
        result = repay_loan(mc_ign, loan_id, amount)
        embed = discord.Embed(
            title="💸 Payment Received!",
            description=result,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed)
        await log_transaction(bot, "Repayment", interaction.user, f"{mc_ign} repaid {amount} diamonds toward Loan #{loan_id}.")

    @tree.command(name="status", description="View your active loans", guild=discord.Object(id=GUILD_ID))
    async def status(interaction: discord.Interaction):
        if not channel_guard(interaction):
            await interaction.response.send_message("🚫 You can’t use that command here.", ephemeral=True)
            return
        mc_ign = get_user_ign(interaction.user.id)
        if not mc_ign:
            await interaction.response.send_message("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return
        result = get_loan_status(mc_ign)
        embed = discord.Embed(
            title=f"📊 Loan Summary for {mc_ign}",
            description=result,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @tree.command(name="loaninfo", description="Admin: Get info about a specific loan ID", guild=discord.Object(id=GUILD_ID))
    async def loaninfo(interaction: discord.Interaction, loan_id: int):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("🚫 You don’t have permission to use this command.", ephemeral=True)
            return
        result = get_loan_details_by_id(loan_id)
        await interaction.response.send_message(result, ephemeral=True)

    @tree.command(name="checkoverdue", description="Check for overdue loans (Admin Only)", guild=discord.Object(id=GUILD_ID))
    async def checkoverdue(interaction: discord.Interaction):
        if not channel_guard(interaction):
            await interaction.response.send_message("🚫 You can’t use that command here.", ephemeral=True)
            return
        overdue = get_overdue_loans()
        if not overdue:
            embed = discord.Embed(
                title="✅ No Overdue Loans!",
                description="Everyone is on time. Great job!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            title="⚠️ Overdue Loans Detected!",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        for loan_id, player_name, due_date in overdue:
            embed.add_field(
                name=f"Loan #{loan_id}",
                value=f"Player: `{player_name}`\nDue Date: `{due_date}`",
                inline=False
            )
        await interaction.response.send_message(embed=embed)
        for loan_id, player_name, due_date in overdue:
            await log_transaction(bot, "Overdue Loan", interaction.user, f"Loan #{loan_id} for {player_name} overdue since {due_date}.")

    @tree.command(name="myid", description="Get your Discord user ID", guild=discord.Object(id=GUILD_ID))
    async def myid(interaction: discord.Interaction):
        await interaction.response.send_message(f"Your Discord ID is `{interaction.user.id}`", ephemeral=True)
