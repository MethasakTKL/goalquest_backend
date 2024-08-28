from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.goals import BaseGoal, Goal
from goalquest_backend.models.users import DBUser
import datetime
from typing import List

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

@router.post("/", response_model = Goal)
async def create_goal(goal: BaseGoal, session: AsyncSession = Depends(get_session)):
    user = await session.get(DBUser, goal.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_goal = Goal(**goal.dict())
    session.add(db_goal)
    await session.commit()
    await session.refresh(db_goal)
    return db_goal

@router.get("/all_goal" , response_model=List[BaseGoal])
async def read_all_goals(session: AsyncSession = Depends(get_session)):
    goal = await session.execute(select(Goal))
    goal_list = goal.scalars().all()
    return goal_list

@router.get("/{goal_id}", response_model = Goal)
async def read_goal(goal_id: int, session: AsyncSession = Depends(get_session)):
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.put("/{goal_id}", response_model = Goal)
async def update_goal(goal_id : int, goal_update : BaseGoal,session: AsyncSession = Depends(get_session)):
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code = 404, detail = "Goal not found")

    goal.title = goal_update.title
    goal.description = goal_update.description
    goal.start_date = goal_update.start_date
    goal.end_date = goal_update.end_date
    goal.updated_at = datetime.datetime.utcnow()

    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal



@router.delete("/{goal_id}", response_model=dict)
async def delete_goal(goal_id: int, session: AsyncSession = Depends(get_session)):
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    await session.delete(goal)
    await session.commit()
    return {"detail": "Goal deleted"}