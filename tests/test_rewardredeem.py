import pytest
from httpx import AsyncClient
from goalquest_backend import models
from sqlalchemy.ext.asyncio import AsyncSession

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

