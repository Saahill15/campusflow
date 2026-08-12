import asyncio
import asyncpg
from pathlib import Path

path = Path('.env')
text = path.read_text(encoding='utf-8')
url = None
for line in text.splitlines():
    if line.strip().startswith('DATABASE_URL='):
        url = line.split('=', 1)[1].strip()
        break
if not url:
    raise SystemExit('DATABASE_URL not found')

async def main():
    conn = await asyncpg.connect(dsn=url, ssl='require')
    try:
        ev_count = await conn.fetchval("SELECT COUNT(*) FROM events WHERE slug = 'pragyarambh-2026'")
        print('event_slug=pragyarambh-2026')
        print('event_count=' + str(ev_count))

        print('recent_registrations=')
        rows = await conn.fetch("SELECT registration_number, status FROM registrations ORDER BY created_at DESC LIMIT 10")
        for row in rows:
            print(f"  {row['registration_number']} {row['status']}")

        last = await conn.fetchval("SELECT registration_number FROM registrations WHERE registration_number LIKE 'PG26-%' ORDER BY registration_number DESC LIMIT 1")
        print('last_pg26_registration_number=' + str(last))

        print('registration_constraints=')
        constraints = await conn.fetch("SELECT conname, contype, pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conrelid = 'registrations'::regclass ORDER BY conname")
        for row in constraints:
            print(f"  {row['conname']} {row['contype']} {row['definition']}")

        print('registration_indexes=')
        indexes = await conn.fetch("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='registrations' ORDER BY indexname")
        for row in indexes:
            print(f"  {row['indexname']} {row['indexdef']}")
    finally:
        await conn.close()

asyncio.run(main())
