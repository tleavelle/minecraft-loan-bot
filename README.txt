# Minecraft Loan Bot 💎

A slash-command-based Discord bot for managing diamond loans in your Minecraft server — integrated with a custom SQLite backend, per-user permissions, auto-generated loan agreements, and logging.

---

## 🔧 Features

- Apply for in-game loans with `/apply`
- Repay loans using `/repay`
- View your loan status using `/status`
- Auto-DMs players a signed loan agreement
- Admin-only linking of Minecraft IGNs to Discord accounts via `/linkuser`
- Logs all transactions to file (and optionally to a Discord channel)
- Detects and reports overdue loans with `/checkoverdue`

---

## 📁 File Structure

```
minecraft-loan-bot/
├── bot.py             # Main bot startup (slash commands enabled)
├── config.py          # Token, owner ID, allowed channel(s), and optional log channel
├── db.py              # Database connection and table setup
├── users.py           # User linking logic
├── loans.py           # Loan, repayment, and overdue logic
├── igns.py            # Minecraft IGN list loader
├── logger.py          # Logs all bot activity
├── commands.py        # All slash command handlers
├── logs/              # Transaction logs
├── Loan Agreements/   # Auto-generated loan agreement .txt files
├── .gitignore         # Keeps secrets and sensitive files out of Git
```

---

## 🚀 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/minecraft-loan-bot.git
   cd minecraft-loan-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot**
   Edit `config.py`:
   ```python
   DISCORD_TOKEN = "your-bot-token"
   OWNER_ID = 123456789012345678  # your Discord user ID
   ALLOWED_CHANNELS = [987654321012345678,1234567890987654321]  # allowed text channel(s) recommend a loan-manager channel for using the app, and a loan-logs channel.
   LOG_CHANNEL_ID = 123456789012345678  # optional: for logging actions to a Discord channel
   ```

4. **Run the bot**
   ```bash
   python3 bot.py
   ```

---

## 🧾 Slash Commands

| Command                    | Description                                      |
|----------------------------|--------------------------------------------------|
| `/apply amount`            | Request a loan of X diamonds                    |
| `/repay loan_id amount`    | Repay part or all of a loan                    |
| `/status`                  | View your active loans                         |
| `/myid`                    | Get your Discord user ID                       |
| `/linkuser user ign`       | *(Admin only)* Link a user to a Minecraft IGN  |
| `/checkoverdue`            | *(Admin only)* List all overdue loans          |

---

## ⚙️ Requirements

- Python 3.9+
- `discord.py` 2.3+ **or** [`py-cord`](https://pypi.org/project/py-cord/) 2.5+

Install `py-cord` (recommended for stability):
```bash
pip install py-cord
```

---

## 📜 License

MIT License — use freely, credit appreciated!
