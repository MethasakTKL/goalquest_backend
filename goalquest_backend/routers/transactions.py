from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.rewards import Reward
from goalquest_backend.models.reward_history import RewardHistory
import datetime
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.post("/")
async def redeem_reward(point_id: int, reward_id: int, session: AsyncSession = Depends(get_session)):
    # Check if point record exists
    point_record = await session.execute(select(Point).where(Point.point_id == point_id))
    point_record = point_record.scalar_one_or_none()
    if not point_record:
        raise HTTPException(status_code=404, detail="Point record not found")

    # Check if the reward exists
    reward = await session.execute(select(Reward).where(Reward.reward_id == reward_id))
    reward = reward.scalar_one_or_none()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Check if user has enough points
    if point_record.total_point < reward.points_required:
        raise HTTPException(status_code=400, detail="Insufficient points for this reward")

    # Update user points
    point_record.total_point -= reward.points_required
    await session.commit()

    # Record reward redemption
    reward_history = RewardHistory(
        user_id=point_record.user_id,  # Assuming Point model has a user_id field
        reward_id=reward_id,
        points_spent=reward.points_required,
        transaction_date=datetime.datetime.utcnow()  # Set current time
    )
    session.add(reward_history)
    await session.commit()

    return {"message": "Reward redeemed successfully", "reward_id": reward_id, "points_spent": reward.points_required}