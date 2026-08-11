import sqlite3
from pathlib import Path

path = Path('migration_test.db')
print('DB path:', path.resolve())
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print('tables:', [row[0] for row in cur.fetchall()])
for row in cur.execute("SELECT id, registration_number, status, email, roll_number, phone, rejected_reason, approved_at, approved_by, created_at FROM registrations WHERE email = ?", ('sahililiyaskhan@gmail.com',)):
    print(row)
conn.close()
