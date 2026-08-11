import asyncio
import httpx
import uuid
import os

BASE = os.environ.get('BACKEND_URL', 'http://127.0.0.1:8000')


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        # 1. health
        try:
            r = await client.get('/health')
            print('HEALTH', r.status_code, r.text[:200])
        except Exception as e:
            print('Health check failed:', e)
            return

        # 2. create registration
        email = f'debug{uuid.uuid4().hex[:6]}@example.com'
        payload = {
            'first_name': 'Debug',
            'last_name': 'User',
            'email': email,
            'department': 'CS',
            'academic_year': '3',
            'roll_number': 'D' + uuid.uuid4().hex[:6],
            'phone': '9999999999',
            'gender': 'other'
        }
        r = await client.post('/api/v1/registration', json=payload)
        print('CREATE REG', r.status_code, r.text)

        # 3. admin login
        admin_email = os.environ.get('DEBUG_ADMIN_EMAIL', 'sahil@mail.com')
        admin_password = os.environ.get('DEBUG_ADMIN_PASSWORD', 'password')
        r = await client.post('/auth/login', json={'email': admin_email, 'password': admin_password})
        print('ADMIN LOGIN', r.status_code, r.text)
        if r.status_code != 200:
            print('Cannot login as admin')
            return
        token = r.json().get('data', {}).get('access_token')
        headers = {'Authorization': f'Bearer {token}'}

        # 4. list registrations to find our item
        params = {'search': email}
        r = await client.get('/api/v1/admin/registrations', headers=headers, params=params)
        print('ADMIN LIST', r.status_code)
        print(r.text)
        items = r.json().get('items', [])
        if not items:
            print('No admin-listed registrations found')
            return
        reg = items[0]
        reg_id = reg.get('id')
        print('Found registration id:', reg_id)

        # 5. open admin detail
        r = await client.get(f'/api/v1/admin/registrations/{reg_id}', headers=headers)
        print('ADMIN DETAIL GET', r.status_code, r.text)

        # 6. approve via API (capture request/response)
        r = await client.post(f'/api/v1/admin/registrations/{reg_id}/approve', headers=headers)
        print('APPROVE POST', r.status_code, r.text)

        # 7. check pass GET
        r = await client.get(f'/api/v1/admin/registrations/{reg_id}/pass', headers=headers)
        print('GET PASS', r.status_code, r.text[:1000])

        # 8. inspect DB via list (passes), but we can't access DB directly here. Rely on API outputs.

if __name__ == '__main__':
    asyncio.run(main())
