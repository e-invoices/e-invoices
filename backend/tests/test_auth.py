import pytest
from app.core.security import decode_access_token


@pytest.mark.asyncio
async def test_register_and_login(api_client):
    payload = {
        "email": "auth@example.com",
        "password": "secret",
        "full_name": "Auth User",
    }
    response = await api_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    assert access_token

    decoded = decode_access_token(access_token)
    assert decoded["sub"]

    form_data = {"username": payload["email"], "password": payload["password"]}
    response = await api_client.post("/api/v1/auth/token", data=form_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(api_client):
    payload = {
        "email": "dupe-auth@example.com",
        "password": "secret",
        "full_name": "Auth User",
    }
    first = await api_client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    duplicate = await api_client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_invalid_credentials(api_client):
    payload = {
        "email": "invalid@example.com",
        "password": "secret",
        "full_name": "Auth User",
    }
    await api_client.post("/api/v1/auth/register", json=payload)
    form_data = {"username": payload["email"], "password": "wrong"}
    response = await api_client.post("/api/v1/auth/token", data=form_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
