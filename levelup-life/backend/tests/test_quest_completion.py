import pytest
import uuid
from httpx import AsyncClient
from datetime import date

pytestmark = pytest.mark.asyncio

VALID_USER = {
    "email": "hero@questtest.com",
    "username": "QuestHero",
    "password": "StrongPass123",
}

OTHER_USER = {
    "email": "other@questtest.com",
    "username": "OtherUser",
    "password": "StrongPass123",
}

QUEST_PAYLOAD = {
    "title": "Morning Run",
    "description": "Run 5km before breakfast",
    "domain": "fitness",
    "difficulty": "medium",
    "xp_reward": 150,
    "stat_rewards": {"strength": 2, "endurance": 3},
    "estimated_duration": "30 min",
    "context_tags": ["running", "cardio"],
}


async def register_and_login(client: AsyncClient, user: dict) -> str:
    resp = await client.post("/api/v1/auth/register", json=user)
    assert resp.status_code == 201
    return resp.json()["access_token"]


async def create_quest(client: AsyncClient, token: str, payload: dict = None) -> dict:
    data = payload or QUEST_PAYLOAD
    resp = await client.post(
        "/api/v1/quests/",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def test_complete_quest_returns_xp(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["xp_gained"] == QUEST_PAYLOAD["xp_reward"]
    assert data["new_total_xp"] == QUEST_PAYLOAD["xp_reward"]


async def test_complete_quest_updates_stats(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "updated_stats" in data
    assert data["updated_stats"].get("strength") == 2
    assert data["updated_stats"].get("endurance") == 3


async def test_complete_quest_level_up(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token, {
        **QUEST_PAYLOAD,
        "xp_reward": 500,
    })

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_level"] >= 2
    assert data["leveled_up"] is True


async def test_complete_quest_twice_returns_400(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "already completed" in resp.json()["detail"].lower()


async def test_complete_nonexistent_quest_returns_404(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    fake_id = str(uuid.uuid4())

    resp = await client.post(
        f"/api/v1/quests/{fake_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_complete_other_users_quest_returns_404(client: AsyncClient):
    token_a = await register_and_login(client, VALID_USER)
    token_b = await register_and_login(client, OTHER_USER)

    quest = await create_quest(client, token_a)

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


async def test_complete_quest_streak_info(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    resp = await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "streak_info" in data
    assert "current_streak" in data["streak_info"]
    assert "message" in data["streak_info"]
    assert data["streak_info"]["current_streak"] >= 0


async def test_complete_quest_updates_user_xp(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    await client.post(
        f"/api/v1/quests/{quest['id']}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    me_resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    assert user_data["total_xp"] == QUEST_PAYLOAD["xp_reward"]
    assert user_data["total_quests_completed"] == 1


async def test_create_and_delete_quest(client: AsyncClient):
    token = await register_and_login(client, VALID_USER)
    quest = await create_quest(client, token)

    resp = await client.delete(
        f"/api/v1/quests/{quest['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


async def test_delete_other_users_quest_returns_404(client: AsyncClient):
    token_a = await register_and_login(client, VALID_USER)
    token_b = await register_and_login(client, OTHER_USER)

    quest = await create_quest(client, token_a)

    resp = await client.delete(
        f"/api/v1/quests/{quest['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


async def test_quest_history_only_returns_own_quests(client: AsyncClient):
    token_a = await register_and_login(client, VALID_USER)
    token_b = await register_and_login(client, OTHER_USER)

    await create_quest(client, token_a)
    await create_quest(client, token_b)

    resp = await client.get(
        "/api/v1/quests/history",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == 200
    quests = resp.json()
    assert len(quests) == 1
    assert all(q["user_id"] != str(uuid.UUID(int=0)) for q in quests)
