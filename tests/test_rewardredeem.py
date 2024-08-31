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
    response = await client.post("/redeems/{example_reward1.reward_id}", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_successful_redemption(
    client: AsyncClient, 
    token_user1: models.Token, 
    example_reward1: Reward, 
    session: AsyncSession
):
    # Perform the redemption request
    response = await client.post(
        f"/redeems/{example_reward1.reward_id}",
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reward redeemed successfully"
    assert data["reward_id"] == example_reward1.reward_id
    assert data["points_spent"] == example_reward1.points_required

    point_record = await session.execute(
        select(Point).where(Point.user_id == token_user1.user_id)
    )
    point_record = point_record.scalar_one_or_none()
    assert point_record is not None

