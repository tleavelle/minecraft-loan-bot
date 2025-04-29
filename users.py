# users.py

from db import get_connection
from igns import load_igns

def link_user(discord_id: int, mc_ign: str) -> str:
    igns = load_igns()
    if mc_ign not in igns:
        return "❌ That IGN isn't in the list. Add it to igns.txt first."

    conn = get_connection()
    cursor = conn.cursor()

    # Check if IGN or Discord ID already linked
    cursor.execute("SELECT * FROM linked_users WHERE discord_id = ? OR mc_ign = ?", (str(discord_id), mc_ign))
    existing = cursor.fetchone()

    if existing:
        return "⚠️ That Discord user or IGN is already linked."

    cursor.execute("INSERT INTO linked_users (discord_id, mc_ign) VALUES (?, ?)", (str(discord_id), mc_ign))
    conn.commit()
    conn.close()
    return f"✅ Linked <@{discord_id}> to `{mc_ign}` successfully."

def get_user_ign(discord_id: int) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mc_ign FROM linked_users WHERE discord_id = ?", (str(discord_id),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
