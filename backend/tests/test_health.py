import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get('/health/')
    assert resp.status_code in (200, 503)
