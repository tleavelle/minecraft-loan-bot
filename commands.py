# commands.py

import discord
from discord.ext import commands
from config import OWNER_ID
from igns import load_igns
from users import link_user, get_user_ign
from loans import apply_for_loan, repay_loan, get_loan_status

igns_set = set(load_igns())

def setup_commands(bot):

    @bot.command(name="linkuser")
    async def linkuser(ctx, member: discord.Member, ign: str):
        if ctx.author.id != OWNER_ID:
            await ctx.send("🚫 You don’t have permission to use this command.")
            return

        ign = ign.strip()
        result = link_user(member.id, ign)
        await ctx.send(result)

    @bot.command(name="apply")
    async def apply(ctx, amount: int):
        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return
        if amount <= 0:
            await ctx.send("❌ Invalid loan amount.")
            return

        result = apply_for_loan(mc_ign, amount)
        await ctx.send(result)

    @bot.command(name="repay")
    async def repay(ctx, loan_id: int, amount: float):
        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return

        result = repay_loan(mc_ign, loan_id, amount)
        await ctx.send(result)

    @bot.command(name="status")
    async def status(ctx):
        mc_ign = get_user_ign(ctx.author.id)
        if not mc_ign:
            await ctx.send("⚠️ You're not linked. Ask the admin to run `!linkuser` for you.")
            return

        result = get_loan_status(mc_ign)
        await ctx.send(result)

    @bot.command(name="myid")
    async def myid(ctx):
        await ctx.send(f"Your Discord ID is `{ctx.author.id}`")

    @bot.command(name="helpme")
    async def helpme(ctx):
        await ctx.send("""
📖 **LoanBot Commands**
`!apply <amount>` – Request a diamond loan
`!repay <loan_id> <amount>` – Repay a loan
`!status` – View your active loans
`!myid` – Get your Discord ID

🔒 Admin Only:
`!linkuser @user <mc_ign>` – Link a Discord user to a Minecraft IGN
        """)
