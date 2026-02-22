import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

pytestmark = pytest.mark.asyncio


VALID_USER = {
    "email": "hero@example.com",
    "username": "HeroUser",
    "password": "StrongPass123",
}


async def register_user(client: AsyncClient, user: dict = None) -> dict:
    payload = user or VALID_USER
    resp = await client.post("/api/v1/auth/register", json=payload)
    return resp


async def test_register_success(client: AsyncClient):
    resp = await register_user(client)
    assert resp.status_code == 201
    data = resp.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == VALID_USER["email"]
    assert data["user"]["username"] == VALID_USER["username"]
    assert "hashed_password" not in data["user"]


async def test_register_duplicate_email(client: AsyncClient):
    await register_user(client)
    resp = await register_user(client)
    assert resp.status_code == 409


async def test_login_success(client: AsyncClient):
    await register_user(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == VALID_USER["email"]


async def test_login_bad_password(client: AsyncClient):
    await register_user(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": VALID_USER["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient):
    reg = await register_user(client)
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


async def test_protected_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code in (401, 403)


async def test_protected_expired_token(client: AsyncClient):
    await register_user(client)
    expired_payload = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        "type": "access",
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
