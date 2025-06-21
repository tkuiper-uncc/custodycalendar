# backup_seed_generator.py

import sqlite3

conn = sqlite3.connect("custody_calendar.db")
cursor = conn.cursor()

cursor.execute("SELECT date, parent, note FROM assignments")
rows = cursor.fetchall()
conn.close()

with open("seed_assignments.py", "w") as f:
    f.write("seed_data = [\n")
    for row in rows:
        f.write(f"    {row!r},\n")
    f.write("]\n")

print("✅ Backup complete: seed_assignments.py created.")
