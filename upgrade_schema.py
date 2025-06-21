# run this once to add the 'note' column to your table
import sqlite3

conn = sqlite3.connect("custody_calendar.db")
cursor = conn.cursor()

# Add 'note' column if it doesn't already exist
try:
    cursor.execute("ALTER TABLE assignments ADD COLUMN note TEXT")
    print("✅ 'note' column added to assignments table.")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("ℹ️ 'note' column already exists.")
    else:
        raise

conn.commit()
conn.close()
