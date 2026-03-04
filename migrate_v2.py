"""
Migration script for Phase 1 V2 Database Overhaul.
Recreates the users table with the new 5-pose encoding columns,
and creates the new tables for Sessions, Logs, and Disputes.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "attendance.db")

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Starting database migration for V2...")

    # 1. Create ClassSessions table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS class_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR,
            start_time DATETIME,
            end_time DATETIME,
            is_active BOOLEAN
        )
    ''')

    # 2. Upgrade Users table
    # SQLite does not support multiple ADD COLUMN well in older versions, 
    # but since this is a dev DB, we will just add them individually.
    cur.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cur.fetchall()]

    if "face_encoding_front" not in user_columns:
        print("Migrating users table...")
        # Since 'face_encoding' was the old required column, we need to alter it or map it.
        # SQLite doesn't easily let us rename columns in ancient ways, 
        # so let's just add the 4 new ones and rename the old one in python logic if needed, 
        # but here we can just add them.
        cur.execute("ALTER TABLE users RENAME COLUMN face_encoding TO face_encoding_front")
        cur.execute("ALTER TABLE users ADD COLUMN face_encoding_left BLOB")
        cur.execute("ALTER TABLE users ADD COLUMN face_encoding_right BLOB")
        cur.execute("ALTER TABLE users ADD COLUMN face_encoding_up BLOB")
        cur.execute("ALTER TABLE users ADD COLUMN face_encoding_down BLOB")
        cur.execute("ALTER TABLE users ADD COLUMN confidence_threshold FLOAT")

    # 3. Upgrade Attendance table
    cur.execute("PRAGMA table_info(attendance_logs)")
    att_columns = [row[1] for row in cur.fetchall()]
    if "session_id" not in att_columns:
        print("Migrating attendance table...")
        cur.execute("ALTER TABLE attendance_logs ADD COLUMN session_id INTEGER")
        cur.execute("ALTER TABLE attendance_logs ADD COLUMN confidence_score FLOAT")

    # 4. Create AuditLogs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action VARCHAR NOT NULL,
            details TEXT,
            timestamp DATETIME,
            ip_address VARCHAR
        )
    ''')

    # 5. Create SpoofLogs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS spoof_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            reason VARCHAR,
            capture_image BLOB,
            session_id INTEGER
        )
    ''')

    # 6. Create Disputes
    cur.execute('''
        CREATE TABLE IF NOT EXISTS disputes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            attendance_log_id INTEGER,
            reason TEXT NOT NULL,
            status VARCHAR DEFAULT 'Pending',
            timestamp DATETIME
        )
    ''')

    conn.commit()
    conn.close()
    print("Migration successful.")

if __name__ == "__main__":
    run_migration()
