from httpx import AsyncClient
from goalquest_backend import models
import pytest

@pytest.mark.asyncio
async def test_create_reward(
    client: AsyncClient,
    user1: models.DBUser,
):
    payload = {
        "title": "Test Reward",
        "description": "Test reward description",
        "points_required": 100
    }

    response = await client.post("/rewards/", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_reward(client: AsyncClient, session, example_reward1):
    reward_id = example_reward1.reward_id
    updated_data = {
        "title": "Updated Reward Title",
        "description": "Updated Description",
        "points_required": 200
    }

    response = await client.put(f"/rewards/{reward_id}", json=updated_data)
    
    assert response.status_code == 200
    updated_reward = response.json()

    assert updated_reward["title"] == updated_data["title"]
    assert updated_reward["description"] == updated_data["description"]
    assert updated_reward["points_required"] == updated_data["points_required"]

@pytest.mark.asyncio
async def test_delete_reward2(client: AsyncClient, example_reward2: models.Reward):
    reward_id = example_reward2.reward_id

    response = await client.delete(f"/rewards/{reward_id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["detail"] == "Reward deleted"

