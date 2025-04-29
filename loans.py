# loans.py

import math
import os
from datetime import datetime, timedelta
from db import get_connection

def apply_for_loan(mc_ign: str, amount: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(loan_amount) FROM loans WHERE player_name = ?", (mc_ign,))
    current_total = cursor.fetchone()[0] or 0

    if current_total + amount > 128:
        conn.close()
        return f"❌ Cannot loan {amount}. You can only borrow up to {128 - current_total} more diamonds."

    fee = amount * 0.05
    total_owed = math.ceil(amount + fee)
    date_borrowed = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")

    cursor.execute('''
        INSERT INTO loans (player_name, loan_amount, date_borrowed, due_date, fee, total_owed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (mc_ign, amount, date_borrowed, due_date, fee, total_owed))
    conn.commit()

    loan_id = cursor.lastrowid
    agreements_dir = "Loan Agreements"
    os.makedirs(agreements_dir, exist_ok=True)
    agreement_path = os.path.join(agreements_dir, f"Loan_Agreement_{mc_ign}_{loan_id}.txt")

    with open(agreement_path, "w") as file:
        file.write(f"""=== Minecraft Diamond Loan Agreement ===
Loan ID: {loan_id}
Player: {mc_ign}
Date of Agreement: {date_borrowed}
Loan Amount (Principal): {amount} diamonds
Flat Fee (5%): {fee:.2f} diamonds
Total Owed: {total_owed} diamonds
Due Date: {due_date}

--- Terms & Conditions ---
Repayment must be made in full before the due date.
Partial diamonds are not accepted. No exceptions.

Failure to repay may result in:
- Repossession of diamond-based assets
- Confiscation of enchanted tools
- Public shaming via server-wide announcements

Signature: ___________________________
Bank Representative: The Vaultkeeper
""")

    conn.close()
    return f"✅ Loan approved for `{mc_ign}`: {amount} diamonds (+ fee = {total_owed}). Due: {due_date}."

def get_loan_status(mc_ign: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT loan_amount, amount_repaid, total_owed, due_date FROM loans WHERE player_name = ?", (mc_ign,))
    loans = cursor.fetchall()
    conn.close()

    if not loans:
        return f"🟢 `{mc_ign}` has no active loans."

    msg = f"📊 Loan summary for `{mc_ign}`:\n"
    for i, loan in enumerate(loans, 1):
        loan_amt, repaid, total, due = loan
        remaining = total - repaid
        msg += f"\n**Loan {i}:**\n" \
               f"> Principal: {loan_amt} 💎\n" \
               f"> Repaid: {repaid} 💎\n" \
               f"> Total Owed: {total} 💎\n" \
               f"> Remaining: {remaining:.2f} 💎\n" \
               f"> Due: {due}\n"
    return msg

def repay_loan(mc_ign: str, loan_id: int, amount: float) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total_owed, amount_repaid FROM loans WHERE id = ? AND player_name = ?", (loan_id, mc_ign))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return "❌ Loan not found."

    total_owed, repaid = loan
    remaining = total_owed - repaid
    if amount > remaining:
        conn.close()
        return f"⚠️ You only owe {remaining:.2f} diamonds."

    cursor.execute("UPDATE loans SET amount_repaid = amount_repaid + ? WHERE id = ?", (amount, loan_id))
    cursor.execute("INSERT INTO repayments (loan_id, amount, date) VALUES (?, ?, ?)",
                   (loan_id, amount, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

    cursor.execute("SELECT amount_repaid, total_owed FROM loans WHERE id = ?", (loan_id,))
    repaid, total = cursor.fetchone()
    if math.ceil(repaid) >= total:
        cursor.execute('''
            INSERT INTO loan_archive (id, player_name, loan_amount, date_borrowed, due_date, date_repaid)
            SELECT id, player_name, loan_amount, date_borrowed, due_date, ?
            FROM loans WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d"), loan_id))
        cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
        conn.commit()
        conn.close()
        return f"✅ Payment recorded. Loan {loan_id} fully repaid and archived."

    conn.close()
    return f"✅ Payment of {amount} diamonds applied to Loan {loan_id}."

