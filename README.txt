# Minecraft Loan Bot 💎

A command-based Discord bot for managing diamond loans in your Minecraft server — integrated with a custom SQLite backend and per-user permissions.

## 🔧 Features

- Apply for in-game loans with `!apply <amount>`
- Repay loans using `!repay <loan_id> <amount>`
- View your loan status with `!status`
- Admin-only linking of Minecraft IGNs to Discord accounts via `!linkuser`

## 📁 File Structure

```
loanbot/
├── bot.py             # Main bot startup
├── config.py          # Token and owner ID (keep private!)
├── db.py              # Database connection and table setup
├── users.py           # User linking logic
├── loans.py           # Loan and repayment logic
├── igns.py            # MC IGN validation
├── commands.py        # All Discord command handlers
├── .gitignore         # Keeps secrets and db out of GitHub
```

## 🚀 Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/tleavelle/minecraft-loan-bot.git
   cd minecraft-loan-bot
   ```

2. Install requirements:
   ```bash
   pip install discord.py
   ```

3. Add your bot token and Discord ID to `config.py`:
   ```python
   DISCORD_TOKEN = "your-bot-token-here"
   OWNER_ID = 123456789012345678  # your Discord user ID
   ```

4. Run the bot:
   ```bash
   python3 bot.py
   ```

## 👮 Admin Commands

| Command | Description |
|--------|-------------|
| `!linkuser @user IGN` | Link a Discord user to their Minecraft IGN (admin-only) |
| `!myid`               | Get your Discord user ID |
| `!helpme`             | See all available commands |

## 📜 License

MIT License. Use freely, credit appreciated!

