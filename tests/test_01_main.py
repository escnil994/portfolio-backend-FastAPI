import pytest

@pytest.mark.asyncio
async def test_la_api_responde(client):

    response = await client.get("/")

    print(f"\nLa API respondió con código: {response.status_code}")
    assert response.status_code != 500