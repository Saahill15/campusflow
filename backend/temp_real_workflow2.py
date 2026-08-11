import asyncio
import json
import os
from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app

ADMIN_EMAIL = 'sahil@mail.com'
ADMIN_PASSWORD = 'password'
TEST_EMAIL_REGISTRATION = 'writetosahilkhan@gmail.com'
TEST_EMAIL_APPROVAL = 'sahililiyaskhan@gmail.com'

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

        print('\nTEST 1 — REAL REGISTRATION')
        payload1 = {
            'first_name': 'Sahil',
            'last_name': 'Ilyas',
            'department': 'Computer Science',
            'academic_year': 'Second Year',
            'roll_number': f'FCS26{os.urandom(4).hex()}',
            'phone': '9999999999',
            'email': TEST_EMAIL_REGISTRATION,
            'gender': 'Male',
        }
        reg_resp1 = await client.post('/api/v1/registration', json=payload1)
        print('registration create status', reg_resp1.status_code)
        print(reg_resp1.text)
        registration1 = reg_resp1.json() if reg_resp1.status_code == 200 else None

        reg_id1 = None
        if registration1:
            reg_id1 = registration1.get('registration_number')
            print('registration_number', registration1.get('registration_number'))
            print('status', registration1.get('status'))
            print('confirmation_email_sent', registration1.get('confirmation_email_sent'))

            list_resp = await client.get('/api/v1/admin/registrations', headers=headers, params={'per_page': 100})
            if list_resp.status_code == 200:
                for item in list_resp.json().get('items', []):
                    if item.get('email') == TEST_EMAIL_REGISTRATION and item.get('roll_number') == payload1['roll_number']:
                        reg_id1 = item['id']
                        break
            print('resolved first registration id', reg_id1)

        print('\nTEST 2 — REAL REJECTION')
        reject_response = None
        if reg_id1:
            reject_resp = await client.post(f'/api/v1/admin/registrations/{reg_id1}/reject', headers=headers, json={'reason': 'Test rejection — Pragyarambh 2026 email delivery verification.'})
            print('reject status', reject_resp.status_code)
            print(reject_resp.text)
            if reject_resp.status_code == 200:
                reject_response = reject_resp.json()
                print('rejected status', reject_response.get('status'))
                print('rejected_reason', reject_response.get('rejected_reason'))
                print('notification_email_sent', reject_response.get('notification_email_sent'))
        else:
            print('No registration id available for rejection.')

        print('\nTEST 3 — REAL APPROVAL')
        payload2 = {
            'first_name': 'Sahil',
            'last_name': 'Ilyas',
            'department': 'Computer Science',
            'academic_year': 'Second Year',
            'roll_number': f'FCS26{os.urandom(4).hex()}',
            'phone': '9999999998',
            'email': TEST_EMAIL_APPROVAL,
            'gender': 'Male',
        }
        reg_resp2 = await client.post('/api/v1/registration', json=payload2)
        print('second registration create status', reg_resp2.status_code)
        print(reg_resp2.text)
        registration2 = reg_resp2.json() if reg_resp2.status_code == 200 else None

        reg_id2 = None
        if registration2:
            list_resp2 = await client.get('/api/v1/admin/registrations', headers=headers, params={'per_page': 100})
            if list_resp2.status_code == 200:
                for item in list_resp2.json().get('items', []):
                    if item.get('email') == TEST_EMAIL_APPROVAL and item.get('phone') == payload2['phone']:
                        reg_id2 = item['id']
                        break
            print('resolved second registration id', reg_id2)

        approve_response = None
        if reg_id2:
            approve_resp = await client.post(f'/api/v1/admin/registrations/{reg_id2}/approve', headers=headers)
            print('approve status', approve_resp.status_code)
            print(approve_resp.text)
            if approve_resp.status_code == 200:
                approve_response = approve_resp.json()
                print('approval notification_email_sent', approve_response.get('notification_email_sent'))
        else:
            print('No second registration id available for approval.')

        print('\nDUPLICATE PROTECTION CHECKS')
        duplicate_results = {}
        if reg_id1:
            dup_reject = await client.post(f'/api/v1/admin/registrations/{reg_id1}/reject', headers=headers, json={'reason': 'Duplicate attempt'})
            duplicate_results['reject_second_attempt'] = {'status': dup_reject.status_code, 'text': dup_reject.text}
            print('duplicate reject attempt', duplicate_results['reject_second_attempt'])
        if reg_id2:
            dup_approve = await client.post(f'/api/v1/admin/registrations/{reg_id2}/approve', headers=headers)
            duplicate_results['approve_second_attempt'] = {'status': dup_approve.status_code, 'text': dup_approve.text}
            print('duplicate approve attempt', duplicate_results['approve_second_attempt'])

        summary = {
            'registration1_response': registration1,
            'registration1_id': reg_id1,
            'rejection_response': reject_response,
            'registration2_response': registration2,
            'registration2_id': reg_id2,
            'approval_response': approve_response,
            'duplicate_results': duplicate_results,
        }
        print('\nSUMMARY JSON')
        print(json.dumps(summary, indent=2, default=str))

if __name__ == '__main__':
    asyncio.run(main())
