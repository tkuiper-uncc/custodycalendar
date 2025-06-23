def create_table(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS assignments (date TEXT PRIMARY KEY, parent TEXT, note TEXT)""")
    conn.commit()

def get_assignment(conn, date_str):
    c = conn.cursor()
    c.execute("SELECT parent FROM assignments WHERE date = ?", (date_str,))
    result = c.fetchone()
    return result[0] if result else ""

def save_assignment(conn, date_str, parent):
    c = conn.cursor()
    c.execute("SELECT note FROM assignments WHERE date = ?", (date_str,))
    note_result = c.fetchone()
    note = note_result[0] if note_result else ""
    if parent:
        c.execute("REPLACE INTO assignments (date, parent, note) VALUES (?, ?, ?)", (date_str, parent, note))
    else:
        c.execute("DELETE FROM assignments WHERE date = ?", (date_str,))
    conn.commit()

def load_assignments(conn):
    c = conn.cursor()
    c.execute("SELECT date, parent FROM assignments")
    return c.fetchall()

def get_all_assignments(conn):
    return load_assignments(conn)

