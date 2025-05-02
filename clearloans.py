# wipe_loans.py
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM repayments")
cursor.execute("DELETE FROM loans")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='loans'")

conn.commit()
conn.close()

print("✅ All active loans and repayments wiped.")
