import sqlite3
from pathlib import Path

path = Path('migration_test.db')
print('DB path:', path.resolve())
conn = sqlite3.connect(path)
cur = conn.cursor()
print('--- registrations for writetosahilkhan@gmail.com ---')
for row in cur.execute("SELECT id, registration_number, status, email, roll_number, phone, rejected_reason FROM registrations WHERE email = ?", ('writetosahilkhan@gmail.com',)):
    print(row)
print('--- registrations for sahililiyaskhan@gmail.com ---')
for row in cur.execute("SELECT id, registration_number, status, email, roll_number, phone, rejected_reason FROM registrations WHERE email = ?", ('sahililiyaskhan@gmail.com',)):
    print(row)
conn.close()
