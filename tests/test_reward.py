import pytest
from httpx import AsyncClient
from goalquest_backend.models import Reward
from goalquest_backend.models.rewards import BaseReward
from sqlalchemy.ext.asyncio import AsyncSession
from goalquest_backend import config, models, main, security

@pytest.mark.asyncio
async def test_create_reward(session: AsyncSession):
    reward = models.Reward(
        title="New Test Reward",
        description="Description for new test reward",
        points_required=150
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward)

    assert reward.reward_id is not None
    assert reward.title == "New Test Reward"

@pytest.mark.asyncio
async def test_read_reward(session: AsyncSession, example_reward1: models.Reward):
    reward = await session.get(models.Reward, example_reward1.reward_id)
    assert reward is not None
    assert reward.title == example_reward1.title

@pytest.mark.asyncio
async def test_update_reward(session: AsyncSession, example_reward1: models.Reward):
    example_reward1.title = "Updated Test Reward"
    session.add(example_reward1)
    await session.commit()
    await session.refresh(example_reward1)

    assert example_reward1.title == "Updated Test Reward"

@pytest.mark.asyncio
async def test_delete_reward(session: AsyncSession, example_reward1: models.Reward):
    await session.delete(example_reward1)
    await session.commit()

    deleted_reward = await session.get(models.Reward, example_reward1.reward_id)
    assert deleted_reward is None