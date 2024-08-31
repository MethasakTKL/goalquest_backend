from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.rewards import Reward
from goalquest_backend.models.reward_history import RewardHistory
import datetime

from .. import deps
from .. import models

router = APIRouter(
    prefix="/redeems",
    tags=["Redeem rewards [Transaction]"]
)

@router.post("/{reward_id}")
async def redeem_reward(
    reward_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
):
    # Check if point record exists for the current user
    point_record = await session.execute(select(Point).where(Point.user_id == current_user.id))
    point_record = point_record.scalar_one_or_none()
    if not point_record:
        raise HTTPException(status_code=404, detail="Point record not found for the user")

    # Check if the reward exists
    reward = await session.execute(select(Reward).where(Reward.reward_id == reward_id))
    reward = reward.scalar_one_or_none()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Check if user has enough points
    if point_record.total_point < reward.points_required:
        raise HTTPException(status_code=400, detail="Insufficient points for this reward")

    # Check if user has already redeemed this reward
    existing_redemption = await session.execute(
        select(RewardHistory)
        .where(RewardHistory.user_id == current_user.id)
        .where(RewardHistory.reward_id == reward_id)
    )
    existing_redemption = existing_redemption.scalar_one_or_none()
    if existing_redemption:
        raise HTTPException(status_code=400, detail="Reward has already been redeemed by this user")

    # Update user points
    point_record.total_point -= reward.points_required
    await session.commit()

    # Record reward redemption
    reward_history = RewardHistory(
        user_id=current_user.id,  
        reward_id=reward_id,
        points_spent=reward.points_required,
        redeemed_date=datetime.datetime.utcnow()  
    )
    session.add(reward_history)
    await session.commit()

    return {"message": "Reward redeemed successfully", "reward_id": reward_id, "points_spent": reward.points_required}

@router.get("/history")
async def get_reward_history(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
):
    # Query reward history for the current user
    reward_histories = await session.execute(
        select(RewardHistory).where(RewardHistory.user_id == current_user.id)
    )
    reward_histories = reward_histories.scalars().all()

    if not reward_histories:
        raise HTTPException(status_code=404, detail="No reward history found for this user")

    return reward_histories

