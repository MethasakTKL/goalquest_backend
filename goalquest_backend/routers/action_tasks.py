from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.tasks import Task
from typing import Annotated

from .. import deps
from .. import models

router = APIRouter(
    prefix="/actions_task",
    tags=["Actions Task  [Transaction]"]
)

@router.post("/")
async def complete_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
):
    # Fetch point data for the current user
    point = await session.execute(select(Point).where(Point.user_id == current_user.id))
    point = point.scalar_one_or_none()

    if point is None:
        raise HTTPException(status_code=404, detail="Points not found for the current user")

    # Fetch task data
    task = await session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task is already completed
    if task.is_completed:
        return {"message": "Task is already completed, no additional points awarded"}

    # Mark the task as completed and add points
    task.is_completed = True
    session.add(task)
    await session.commit()
    await session.refresh(task)

    #Update the total points for the user
    point.total_point = point.total_point + task.task_point
    session.add(point)
    await session.commit()
    await session.refresh(point)

    return {"message": "Task completed and points added", "points_received": task.task_point}