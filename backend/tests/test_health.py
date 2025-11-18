import pytest


@pytest.mark.asyncio
async def test_health_endpoint(api_client):
    response = await api_client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
