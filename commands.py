import discord
from config import OWNER_ID, ALLOWED_CHANNELS
from igns import load_igns
from users import link_user, get_user_ign
from loans import apply_for_loan, repay_loan, get_loan_status, get_overdue_loans
from logger import log_transaction
from datetime import datetime

igns_set = set(load_igns())

def channel_guard(ctx):
    return ctx.channel.id in ALLOWED_CHANNELS

def setup_commands(bot: discord.Bot):

    @bot.slash_command(description="Link a Discord user to a Minecraft IGN (Admin Only)")
    async def linkuser(ctx: discord.ApplicationContext, user: discord.Member, ign: str):
        if ctx.author.id != OWNER_ID:
            await ctx.respond("🚫 You don’t have permission to use this command.", ephemeral=True)
            return
        if not channel_guard(ctx):
            await ctx.respond("🚫 You can't use that command here.", ephemeral=True)
            return

        result = link_user(user.id, ign.strip())
        await ctx.respond(result)

    @bot.slash_command(description="Apply for a diamond loan")
    async def apply(ctx: discord.ApplicationContext, amount: int):
        if not channel_guard(ctx):
            await ctx.respond("🚫 You can’t use that command here.", ephemeral=True)
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.respond("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return
        if amount <= 0:
            await ctx.respond("❌ Invalid loan amount.", ephemeral=True)
            return

        summary, agreement_path, due_date = apply_for_loan(mc_ign, amount)

        embed = discord.Embed(
            title="✅ Loan Approved!",
            description=summary,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.respond(embed=embed)

        await log_transaction(bot, "Loan Applied", ctx.author, f"{mc_ign} borrowed {amount} diamonds. Due {due_date}.")

        if agreement_path:
            try:
                await ctx.author.send("📄 Here's your loan agreement:", file=discord.File(agreement_path))
            except discord.Forbidden:
                await ctx.respond("⚠️ Could not send loan agreement via DM. Please enable DMs or contact the Vaultkeeper.")

    @bot.slash_command(description="Repay a loan")
    async def repay(ctx: discord.ApplicationContext, loan_id: int, amount: float):
        if not channel_guard(ctx):
            await ctx.respond("🚫 You can’t use that command here.", ephemeral=True)
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.respond("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return

        result = repay_loan(mc_ign, loan_id, amount)

        embed = discord.Embed(
            title="💸 Payment Received!",
            description=result,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.respond(embed=embed)

        await log_transaction(bot, "Repayment", ctx.author, f"{mc_ign} repaid {amount} diamonds toward Loan #{loan_id}.")

    @bot.slash_command(description="View your active loans")
    async def status(ctx: discord.ApplicationContext):
        if not channel_guard(ctx):
            await ctx.respond("🚫 You can’t use that command here.", ephemeral=True)
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.respond("⚠️ You're not linked. Ask the admin to run `/linkuser` for you.", ephemeral=True)
            return

        result = get_loan_status(mc_ign)

        embed = discord.Embed(
            title=f"📊 Loan Summary for {mc_ign}",
            description=result,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        await ctx.respond(embed=embed)

    @bot.slash_command(description="Get your Discord user ID")
    async def myid(ctx: discord.ApplicationContext):
        await ctx.respond(f"Your Discord ID is `{ctx.author.id}`", ephemeral=True)

    @bot.slash_command(description="Check for overdue loans (Admin Only)")
    async def checkoverdue(ctx: discord.ApplicationContext):
        if not channel_guard(ctx):
            await ctx.respond("🚫 You can’t use that command here.", ephemeral=True)
            return

        overdue = get_overdue_loans()

        if not overdue:
            embed = discord.Embed(
                title="✅ No Overdue Loans!",
                description="Everyone is on time. Great job!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await ctx.respond(embed=embed)
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

        await ctx.respond(embed=embed)

        for loan_id, player_name, due_date in overdue:
            await log_transaction(bot, "Overdue Loan", ctx.author, f"Loan #{loan_id} for {player_name} overdue since {due_date}.")
