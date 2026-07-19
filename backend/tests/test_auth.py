import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # register
    resp = await client.post('/auth/register', json={'email': 'test@example.com', 'password': 'securePass123'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data.get('data', {})

    # login
    resp2 = await client.post('/auth/login', json={'email': 'test@example.com', 'password': 'securePass123'})
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert 'access_token' in d2.get('data', {})
    assert 'refresh_token' in d2.get('data', {})
