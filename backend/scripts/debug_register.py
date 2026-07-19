import asyncio
import os
import sys
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./test_auth.db')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from httpx import AsyncClient, ASGITransport


async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        r = await ac.post('/auth/register', json={'email': 'test@example.com', 'password': 'securePass123'})
        print('STATUS', r.status_code)
        try:
            print('JSON:', r.json())
        except Exception:
            print('TEXT:', r.text)


if __name__ == '__main__':
    asyncio.run(main())
