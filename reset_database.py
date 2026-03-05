import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import engine
from sqlalchemy import text

def reset_database():
    print("Clearing database records for a fresh test...")
    with engine.connect() as conn:
        try:
            # We delete in order of dependencies (if any existed, though we are wiping everything)
            conn.execute(text("DELETE FROM disputes;"))
            conn.execute(text("DELETE FROM attendance_logs;"))
            conn.execute(text("DELETE FROM users;"))
            conn.execute(text("DELETE FROM audit_logs;"))
            conn.execute(text("DELETE FROM admins;"))
            conn.commit()
            print("Successfully cleared all admins and users from the database.")
        except Exception as e:
            print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
