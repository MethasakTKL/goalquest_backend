from httpx import AsyncClient
from goalquest_backend import models
import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_read_all_rewards(client: AsyncClient, session: AsyncSession, user1: models.DBUser):

    reward1 = models.Reward(
        title="Reward 1",
        description="Description for Reward 1",
        points_required=100
    )
    reward2 = models.Reward(
        title="Reward 2",
        description="Description for Reward 2",
        points_required=200
    )
    session.add_all([reward1, reward2])
    await session.commit()

    token = "Bearer " + (await client.post("/token", data={"username": user1.username, "password": "123456"})).json()["access_token"]

    response = await client.get("/rewards/allreward", headers={"Authorization": token})

    assert response.status_code == 200


    rewards_list = response.json()
    print(rewards_list)
    assert len(rewards_list) == 2
    assert any(reward["title"] == "Reward 1" for reward in rewards_list)
    assert any(reward["title"] == "Reward 2" for reward in rewards_list)


@pytest.mark.asyncio
async def test_read_reward(client: AsyncClient, session: AsyncSession, user1: models.DBUser):
    reward = models.Reward(
        title="Test Reward",
        description="Test reward description",
        points_required=100
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward) 

    token = "Bearer " + (await client.post("/token", data={"username": user1.username, "password": "123456"})).json()["access_token"]

    response = await client.get(f"/rewards/{reward.reward_id}", headers={"Authorization": token})

    assert response.status_code == 200
    fetched_reward = response.json()

    assert fetched_reward["title"] == reward.title
    assert fetched_reward["description"] == reward.description
    assert fetched_reward["points_required"] == reward.points_required

@pytest.mark.asyncio
async def test_read_reward_not_found(client: AsyncClient, user1: models.DBUser):
    token = "Bearer " + (await client.post("/token", data={"username": user1.username, "password": "123456"})).json()["access_token"]

    response = await client.get("/rewards/999999", headers={"Authorization": token})

    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Reward not found"

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
async def test_update_reward(client: AsyncClient, session: AsyncSession, example_reward1: models.Reward):
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
async def test_delete_reward2(client: AsyncClient, session: AsyncSession, example_reward2: models.Reward):
    reward_id = example_reward2.reward_id

    response = await client.delete(f"/rewards/{reward_id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["detail"] == "Reward deleted"
