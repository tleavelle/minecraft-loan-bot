# loans.py

import math
import os
from datetime import datetime, timedelta
from db import get_connection

def apply_for_loan(mc_ign: str, amount: int) -> tuple[int | None, str, str | None, str | None]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(loan_amount) FROM loans WHERE player_name = ?", (mc_ign,))
    current_total = cursor.fetchone()[0] or 0

    if current_total + amount > 128:
        conn.close()
        return None, f"❌ Cannot loan {amount}. You can only borrow up to {128 - current_total} more diamonds.", None, None

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
    summary = f"✅ `{mc_ign}` has borrowed {amount} diamonds. Total owed: {total_owed} 💎. Due: {due_date}."
    return loan_id, summary, agreement_path, due_date


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
        remaining = math.ceil(total - repaid)
        msg += (
            f"\n**Loan {i}:**\n"
            f"> Principal: {int(loan_amt)} 💎\n"
            f"> Repaid: {int(repaid)} 💎\n"
            f"> Total Owed: {int(total)} 💎\n"
            f"> Remaining: {remaining} 💎\n"
            f"> Due: {due}\n"
        )
    return msg



def repay_loan(mc_ign: str, loan_id: int, amount: float) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total_owed, amount_repaid, due_date FROM loans WHERE id = ? AND player_name = ?", (loan_id, mc_ign))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return "❌ Loan not found."

    total_owed, repaid, due_date = loan
    remaining = total_owed - repaid

    if remaining <= 0:
        conn.close()
        return f"✅ Loan #{loan_id} is already fully repaid."

    if not amount.is_integer():
        conn.close()
        return "❌ You must repay whole diamonds only. No fractions allowed."

    if amount > remaining:
        conn.close()
        return f"❌ Overpayment not allowed. You only owe {remaining:.2f} diamonds."

    cursor.execute("UPDATE loans SET amount_repaid = amount_repaid + ? WHERE id = ?", (amount, loan_id))
    cursor.execute("INSERT INTO repayments (loan_id, amount, date) VALUES (?, ?, ?)",
                   (loan_id, amount, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

    cursor.execute("SELECT amount_repaid, total_owed FROM loans WHERE id = ?", (loan_id,))
    repaid, total = cursor.fetchone()
    remaining_after = total - repaid

    if math.ceil(repaid) >= total:
        cursor.execute('''
            INSERT INTO loan_archive (id, player_name, loan_amount, date_borrowed, due_date, date_repaid)
            SELECT id, player_name, loan_amount, date_borrowed, due_date, ?
            FROM loans WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d"), loan_id))
        cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
        conn.commit()
        conn.close()
        return f"✅ Loan #{loan_id} fully repaid and archived. You're free as a bat in the End!"

    conn.close()
    return f"💸 Payment of {int(amount)} diamonds received for Loan #{loan_id}.\nRemaining balance: {remaining_after:.2f} 💎. Due: {due_date}."



def get_overdue_loans():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id, player_name, due_date FROM loans WHERE due_date < ?", (today,))
    overdue_loans = cursor.fetchall()
    conn.close()
    return overdue_loans


def get_loan_details_by_id(loan_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, loan_amount, fee, total_owed, amount_repaid, date_borrowed, due_date FROM loans WHERE id = ?", (loan_id,))
    loan = cursor.fetchone()
    conn.close()

    if not loan:
        return f"❌ Loan #{loan_id} not found."

    player_name, principal, fee, total_owed, repaid, borrowed, due = loan
    remaining = total_owed - repaid

    return (
        f"📄 **Loan #{loan_id}**\n"
        f"> Player: `{player_name}`\n"
        f"> Principal: {principal} 💎\n"
        f"> Fee: {fee:.2f} 💎\n"
        f"> Total Owed: {total_owed} 💎\n"
        f"> Repaid: {repaid} 💎\n"
        f"> Remaining: {remaining:.2f} 💎\n"
        f"> Borrowed On: {borrowed}\n"
        f"> Due: {due}"
    )
