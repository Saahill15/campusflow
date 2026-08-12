import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        payload = {
            "first_name": "Asha",
            "last_name": "Rai",
            "department": "Cybersecurity and Digital Forensics",
            "academic_year": "First Year",
            "roll_number": "FCS26001",
            "phone": "9876543210",
            "email": "asha@example.com",
            "gender": "Female",
        }
        r = await ac.post('/api/v1/registration', json=payload)
        print('status', r.status_code)
        try:
            print('json', r.json())
        except Exception:
            print('text', r.text)

if __name__ == '__main__':
    asyncio.run(run())
