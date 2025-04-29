import discord
from discord.ext import commands
from config import OWNER_ID, ALLOWED_CHANNELS
from igns import load_igns
from users import link_user, get_user_ign
from loans import apply_for_loan, repay_loan, get_loan_status, get_overdue_loans
from logger import log_transaction
from datetime import datetime  # 🆕 Needed for embed timestamps

igns_set = set(load_igns())

def channel_guard(ctx):
    return ctx.channel.id in ALLOWED_CHANNELS

def setup_commands(bot):

    @bot.command(name="linkuser")
    async def linkuser(ctx, member: discord.Member, ign: str):
        if ctx.author.id != OWNER_ID:
            await ctx.send("🚫 You don’t have permission to use this command.")
            return
        if not channel_guard(ctx):
            await ctx.send("🚫 You can't use that command here.")
            return

        ign = ign.strip()
        result = link_user(member.id, ign)
        await ctx.send(result)

    @bot.command(name="apply")
    async def apply(ctx, amount: int):
        if not channel_guard(ctx):
            await ctx.send("🚫 You can’t use that command here.")
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return
        if amount <= 0:
            await ctx.send("❌ Invalid loan amount.")
            return

        summary, agreement_path, due_date = apply_for_loan(mc_ign, amount)

        embed = discord.Embed(
            title="✅ Loan Approved!",
            description=summary,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)

        await log_transaction(bot, "Loan Applied", ctx.author, f"{mc_ign} borrowed {amount} diamonds. Due {due_date}.")

        if agreement_path:
            try:
                await ctx.author.send("📄 Here's your loan agreement:", file=discord.File(agreement_path))
            except discord.Forbidden:
                await ctx.send("⚠️ Could not send loan agreement via DM. Please enable DMs or contact the Vaultkeeper.")

    @bot.command(name="repay")
    async def repay(ctx, loan_id: int, amount: float):
        if not channel_guard(ctx):
            await ctx.send("🚫 You can’t use that command here.")
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return

        result = repay_loan(mc_ign, loan_id, amount)

        embed = discord.Embed(
            title="💸 Payment Received!",
            description=result,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)

        await log_transaction(bot, "Repayment", ctx.author, f"{mc_ign} repaid {amount} diamonds toward Loan #{loan_id}.")

    @bot.command(name="status")
    async def status(ctx):
        if not channel_guard(ctx):
            await ctx.send("🚫 You can’t use that command here.")
            return

        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return

        result = get_loan_status(mc_ign)

        embed = discord.Embed(
            title=f"📊 Loan Summary for {mc_ign}",
            description=result,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)

    @bot.command(name="myid")
    async def myid(ctx):
        await ctx.send(f"Your Discord ID is `{ctx.author.id}`")

    @bot.command(name="checkoverdue")
    async def checkoverdue(ctx):
        if not channel_guard(ctx):
            await ctx.send("🚫 You can’t use that command here.")
            return

        overdue = get_overdue_loans()

        if not overdue:
            embed = discord.Embed(
                title="✅ No Overdue Loans!",
                description="Everyone is on time. Great job!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="⚠️ Overdue Loans Detected!",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        for loan in overdue:
            loan_id, player_name, due_date = loan
            embed.add_field(
                name=f"Loan #{loan_id}",
                value=f"Player: `{player_name}`\nDue Date: `{due_date}`",
                inline=False
            )

        await ctx.send(embed=embed)

        # Also log overdue warnings
        for loan in overdue:
            loan_id, player_name, due_date = loan
            await log_transaction(bot, "Overdue Loan", ctx.author, f"Loan #{loan_id} for {player_name} overdue since {due_date}.")

    @bot.command(name="helpme")
    async def helpme(ctx):
        embed = discord.Embed(
            title="📖 LoanBot Commands",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Customer Commands", value="""
`!apply <amount>` – Request a diamond loan
`!repay <loan_id> <amount>` – Repay a loan
`!status` – View your active loans
`!myid` – Get your Discord user ID
""", inline=False)
        embed.add_field(name="🔒 Admin Only", value="""
`!linkuser @user <mc_ign>` – Link a Discord user to a Minecraft IGN
`!checkoverdue` – Check for overdue loans
""", inline=False)
        await ctx.send(embed=embed)
