import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), "railway.db")
conn = sqlite3.connect(DB)
conn.execute('''CREATE TABLE IF NOT EXISTS reservations(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 source TEXT NOT NULL,
 destination TEXT NOT NULL,
 travel_date TEXT NOT NULL,
 status TEXT DEFAULT 'CONFIRMED'
)''')
conn.commit()
conn.close()
print("Database initialized:", DB)
