import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import engine
from sqlalchemy import text

def run_migration():
    print("Starting migration to add admin_id to users...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN admin_id INTEGER REFERENCES admins(id)"))
            conn.commit()
            print("Successfully added admin_id column to users table.")
        except Exception as e:
            print(f"Migration error (column might already exist): {e}")

if __name__ == "__main__":
    run_migration()
