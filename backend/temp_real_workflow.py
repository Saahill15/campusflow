import asyncio
import json
import os
from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app

ADMIN_EMAIL = 'sahil@mail.com'
ADMIN_PASSWORD = 'password'
TEST_EMAIL = 'sahililiyaskhan@gmail.com'

async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://local') as client:
        print('ADMIN LOGIN')
        login_resp = await client.post('/auth/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
        print('login status', login_resp.status_code)
        print(login_resp.text)
        if login_resp.status_code != 200:
            return
        token = login_resp.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        print('\nTEST 1 - REAL REGISTRATION')
        payload1 = {
            'first_name': 'Sahil',
            'last_name': 'Ilyas',
            'department': 'Computer Science',
            'academic_year': 'Second Year',
            'roll_number': f'FCS26{os.urandom(4).hex()}',
            'phone': '9999999999',
            'email': TEST_EMAIL,
            'gender': 'Male',
        }
        reg_resp1 = await client.post('/api/v1/registration', json=payload1)
        print('registration create status', reg_resp1.status_code)
        print(reg_resp1.text)
        registration1 = reg_resp1.json() if reg_resp1.status_code == 200 else None

        print('\nLOOKUP FIRST REGISTRATION ID')
        reg_id1 = None
        if registration1:
            list_resp = await client.get('/api/v1/admin/registrations', headers=headers, params={'per_page': 100})
            print('admin registrations list status', list_resp.status_code)
            print(list_resp.text)
            if list_resp.status_code == 200:
                for item in list_resp.json().get('items', []):
                    if item.get('email') == TEST_EMAIL and item.get('status') == 'pending' and item.get('roll_number') == payload1['roll_number']:
                        reg_id1 = item['id']
                        break
            print('first registration id', reg_id1)

        print('\nTEST 2 - REAL REJECTION')
        reject_result = None
        if reg_id1:
            reject_resp = await client.post(f'/api/v1/admin/registrations/{reg_id1}/reject', headers=headers, json={'reason': 'Test rejection — Pragyarambh 2026 email delivery verification.'})
            print('reject status', reject_resp.status_code)
            print(reject_resp.text)
            reject_result = reject_resp.json() if reject_resp.status_code == 200 else None
        else:
            print('No first registration ID available for rejection')

        print('\nTEST 3 - SECOND REGISTRATION (same email)')
        payload2 = {
            'first_name': 'Sahil',
            'last_name': 'Ilyas',
            'department': 'Computer Science',
            'academic_year': 'Second Year',
            'roll_number': f'FCS26{os.urandom(4).hex()}',
            'phone': '9999999998',
            'email': TEST_EMAIL,
            'gender': 'Male',
        }
        reg_resp2 = await client.post('/api/v1/registration', json=payload2)
        print('second registration create status', reg_resp2.status_code)
        print(reg_resp2.text)
        registration2 = reg_resp2.json() if reg_resp2.status_code == 200 else None

        reg_id2 = None
        if registration2:
            list_resp2 = await client.get('/api/v1/admin/registrations', headers=headers, params={'per_page': 100})
            print('admin registrations list 2 status', list_resp2.status_code)
            print(list_resp2.text)
            if list_resp2.status_code == 200:
                for item in list_resp2.json().get('items', []):
                    if item.get('email') == TEST_EMAIL and item.get('status') == 'pending' and item.get('phone') == payload2['phone']:
                        reg_id2 = item['id']
                        break
            print('second registration id', reg_id2)

        print('\nTEST 3 - APPROVAL OF SECOND REGISTRATION')
        approve_result = None
        if reg_id2:
            approve_resp = await client.post(f'/api/v1/admin/registrations/{reg_id2}/approve', headers=headers)
            print('approve status', approve_resp.status_code)
            print(approve_resp.text)
            approve_result = approve_resp.json() if approve_resp.status_code == 200 else None
        else:
            print('No second registration ID available for approval')

        print('\nTEST 4 - DUPLICATE PROTECTION')
        duplicate = {}
        if reg_id1:
            dup_reject_resp = await client.post(f'/api/v1/admin/registrations/{reg_id1}/reject', headers=headers, json={'reason': 'Second reject attempt'})
            duplicate['reject_second_attempt'] = {'status': dup_reject_resp.status_code, 'text': dup_reject_resp.text}
            print('duplicate reject attempt', duplicate['reject_second_attempt'])
        if reg_id2:
            dup_approve_resp = await client.post(f'/api/v1/admin/registrations/{reg_id2}/approve', headers=headers)
            duplicate['approve_second_attempt'] = {'status': dup_approve_resp.status_code, 'text': dup_approve_resp.text}
            print('duplicate approve attempt', duplicate['approve_second_attempt'])

        print('\nSUMMARY JSON')
        summary = {
            'registration1': registration1,
            'registration1_id': reg_id1,
            'reject': reject_result,
            'registration2': registration2,
            'registration2_id': reg_id2,
            'approve': approve_result,
            'duplicate': duplicate,
        }
        print(json.dumps(summary, indent=2, default=str))

if __name__ == '__main__':
    asyncio.run(main())
