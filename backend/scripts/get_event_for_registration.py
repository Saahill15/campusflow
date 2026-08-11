import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parents[1] / 'migration_test.db'
con = sqlite3.connect(str(DB))
cur = con.cursor()
reg_id = '6a6d47f0-bede-4ecd-859f-ec1b0cd78f5f'
cur.execute('SELECT event_id FROM registrations WHERE id=?', (reg_id,))
print('registration', reg_id, 'event_id ->', cur.fetchone())
print('\nEvents table info:')
for c in cur.execute("PRAGMA table_info('events')"): print(c)
print('\nEvents (first 20 ids):')
for r in cur.execute('SELECT id FROM events LIMIT 20'): print(r)
con.close()
