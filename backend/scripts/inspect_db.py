import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'migration_test.db'
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
print('DB path:', DB)
print('\nalembic_version:')
for r in cur.execute("SELECT * FROM alembic_version"): print(r)
print('\nregistrations table info:')
for c in cur.execute("PRAGMA table_info('registrations')"): print(c)
print('\nindexes:')
for i in cur.execute("PRAGMA index_list('registrations')"): print(i)
print('\nlatest registrations:')
for r in cur.execute("SELECT id, registration_number, status, created_at FROM registrations ORDER BY created_at DESC LIMIT 10"): print(r)
print('\npasses:')
for p in cur.execute("SELECT id, pass_number, registration_id, issued_at FROM passes"): print(p)
print('\nqrcodes:')
for q in cur.execute("SELECT id, qr_token, pass_id, generated_at FROM qrcodes"): print(q)
conn.close()
