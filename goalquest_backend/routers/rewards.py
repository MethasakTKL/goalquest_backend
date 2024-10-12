from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.rewards import Reward, BaseReward
from datetime import datetime
from typing import Annotated, List

from .. import deps
from .. import models

router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"]
)

@router.post("/", response_model=Reward)
async def create_reward(reward: BaseReward, session: AsyncSession = Depends(get_session)):
    db_reward = Reward(**reward.dict())
    session.add(db_reward)
    await session.commit()
    await session.refresh(db_reward)
    return db_reward

@router.get("/allreward", response_model=List[Reward])
async def read_all_rewards(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)]
) -> List[Reward]:
    rewards = await session.execute(select(Reward))
    rewards_list = rewards.scalars().all()

    if not rewards_list:
        raise HTTPException(status_code=404, detail="No rewards found")

    # กำหนด exclude ฟิลด์ created_at และ updated_at
    return rewards_list

@router.get("/{reward_id}", response_model=Reward)
async def read_reward(
    reward_id: int, 
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)]
) -> Reward:
    reward = await session.get(Reward, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return reward

@router.put("/{reward_id}", response_model=Reward)
async def update_reward(reward_id: int, reward_update: BaseReward, session: AsyncSession = Depends(get_session)):
    reward = await session.get(Reward, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # อัปเดตข้อมูลรางวัล
    reward.title = reward_update.title
    reward.description = reward_update.description
    reward.points_required = reward_update.points_required
    reward.updated_at = datetime.utcnow()  # อัปเดตเวลาปรับปรุงล่าสุด

    session.add(reward)
    await session.commit()
    await session.refresh(reward)
    return reward

@router.delete("/{reward_id}", response_model=dict)
async def delete_reward(reward_id: int, session: AsyncSession = Depends(get_session)):
    reward = await session.get(Reward, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    await session.delete(reward)
    await session.commit()
    return {"detail": "Reward deleted"}

