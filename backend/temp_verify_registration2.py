import json
import sqlite3
import uuid
import urllib.request
import urllib.error

unique = uuid.uuid4().hex
roll = f'FCS26{unique[:8]}'
email = f'debug{unique}@example.com'
payload = {
    'first_name': 'Debug',
    'last_name': 'Tester',
    'department': 'Cybersecurity and Digital Forensics',
    'academic_year': 'First Year',
    'roll_number': roll,
    'phone': '9999999991',
    'email': email,
    'gender': 'Male',
}
url = 'http://127.0.0.1:8000/api/v1/registration'
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
print('REQUEST URL', url)
print('PAYLOAD', payload)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print('Status', resp.status)
        print('Body', resp.read().decode('utf-8'))
except urllib.error.HTTPError as err:
    print('Status', err.code)
    print('Body', err.read().decode('utf-8'))
except Exception as err:
    print('Error', err)

conn = sqlite3.connect('alembic_test_abs.db')
cur = conn.cursor()
cur.execute("SELECT registration_number, status, first_name, last_name, department, academic_year, roll_number, phone, email, gender FROM registrations WHERE email=?", (email,))
rows = cur.fetchall()
print('DB ROWS', rows)
conn.close()
