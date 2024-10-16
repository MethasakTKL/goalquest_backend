from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.goals import BaseGoal, Goal
from goalquest_backend.models.users import DBUser
from goalquest_backend.models.tasks import Task
import datetime
from typing import Annotated, List

from .. import deps
from .. import models

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

@router.post("/", response_model=Goal)
async def create_goal(
    goal: BaseGoal,     
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> Goal:
    user = await session.get(DBUser, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_goal = Goal(
        title=goal.title,
        description=goal.description,
        progress_percentage= goal.progress_percentage,
        start_date=goal.start_date,
        end_date=goal.end_date,
        is_complete=goal.is_complete,
        user_id=current_user.id,  # Adding user_id explicitly
        created_at=datetime.datetime.utcnow(),  # Add default values if needed
        updated_at=datetime.datetime.utcnow()
    )    
    session.add(db_goal)
    await session.commit()
    await session.refresh(db_goal)
    return db_goal

@router.get("/all_goal", response_model=List[Goal])
async def read_all_goals(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> List[Goal]:
    # ดึง goal ที่เกี่ยวข้องกับผู้ใช้ปัจจุบัน
    goals = await session.execute(select(Goal).where(Goal.user_id == current_user.id))
    goal_list = goals.scalars().all()

    # สำหรับ goal แต่ละอัน ให้ทำการคำนวณว่ามี task เสร็จครบหรือยัง
    for goal in goal_list:
        # ดึง task ที่เกี่ยวข้องกับ goal นั้น
        tasks = await session.execute(select(Task).where(Task.goal_id == goal.goal_id))
        task_list = tasks.scalars().all()

        # นับ task ทั้งหมด และ task ที่เสร็จแล้ว
        total_tasks = len(task_list)
        completed_tasks = len([task for task in task_list if task.is_completed])

        # ตรวจสอบสถานะ goal ว่าเสร็จสมบูรณ์หรือไม่
        if total_tasks > 0 and completed_tasks == total_tasks:
            goal.is_complete = True
        else:
            goal.is_complete = False
        # อัพเดต goal ในฐานข้อมูล
        session.add(goal)
    # commit เพื่ออัพเดตสถานะ goal
    await session.commit()

    return goal_list

@router.get("/{goal_id}", response_model=Goal)
async def read_goal(
    goal_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> Goal:
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this goal")
    return goal

@router.put("/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: int,
    goal_update: BaseGoal,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> Goal:
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this goal")

    goal.title = goal_update.title
    goal.description = goal_update.description
    goal.progress_percentage = goal_update.progress_percentage
    goal.start_date = goal_update.start_date
    goal.end_date = goal_update.end_date
    goal.is_complete = goal_update.is_complete 
    goal.updated_at = datetime.datetime.utcnow()

    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal

@router.delete("/{goal_id}", response_model=dict)
async def delete_goal(
    goal_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this goal")

    await session.delete(goal)
    await session.commit()
    return {"detail": "Goal deleted"}