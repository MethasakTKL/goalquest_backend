import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import Reward, Point, RewardHistory
import datetime
from goalquest_backend import models

import datetime
@pytest.mark.asyncio
async def test_redeem_no_permission(
    client: AsyncClient,
    example_reward1: models.Reward
):
    payload = {
        "reward_id": example_reward1.reward_id
    }
    response = await client.post("/redeems/", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"
@pytest.mark.asyncio
async def test_reward_not_found(
    client: AsyncClient, 
    token_user1: models.Token
):
    non_existent_reward_id = 999999  
    response = await client.post(
        "/redeems/",
        params={"reward_id": non_existent_reward_id},
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )

    assert response.status_code == 404  
    data = response.json()
    assert data["detail"] == "Reward not found"  

@pytest.mark.asyncio
async def test_successful_redemption(
    client: AsyncClient, 
    token_user1: models.Token, 
    example_point_user1: models.Point,
    example_reward1: models.Reward, 
    session: models.AsyncSession
):

    initial_points = example_point_user1.total_point

    response = await client.post(
        "/redeems/",
        params={"reward_id": example_reward1.reward_id},
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reward redeemed successfully"
    assert data["reward_id"] == example_reward1.reward_id
    assert data["points_spent"] == example_reward1.points_required

    await session.refresh(example_point_user1)
    updated_points = example_point_user1.total_point

    expected_points = initial_points - example_reward1.points_required
    assert updated_points == expected_points, f"Expected points to be {expected_points}, but got {updated_points}"


@pytest.mark.asyncio
async def test_insufficient_points_redemption(
    client: AsyncClient, 
    token_user1: models.Token, 
    example_point_user1: models.Point,
    example_reward3: models.Reward,  
    session: models.AsyncSession

):

    initial_points = example_point_user1.total_point

    response = await client.post(
        "/redeems/",
        params={"reward_id": example_reward3.reward_id},
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Insufficient points for this reward"

    await session.refresh(example_point_user1)
    updated_points = example_point_user1.total_point

    assert updated_points == initial_points, f"Expected points to remain {initial_points}, but got {updated_points}"
