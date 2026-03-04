"""
One-time migration: add reset_token and reset_token_expiry columns to the admins table.
Safe to run multiple times — will skip if columns already exist.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "attendance.db")

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

added = []
for col, col_type in [("reset_token", "TEXT"), ("reset_token_expiry", "DATETIME")]:
    if not column_exists(cur, "admins", col):
        cur.execute(f"ALTER TABLE admins ADD COLUMN {col} {col_type}")
        added.append(col)

conn.commit()
conn.close()

if added:
    print(f"✅ Added columns: {', '.join(added)}")
else:
    print("✅ Columns already exist, nothing to change.")
