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
    try:
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

        # Check if task has points to award
        if task.task_point is None or task.task_point <= 0:
            raise HTTPException(status_code=400, detail="Task has no points to award")

        # Mark the task as completed and add points
        task.is_completed = True
        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Update the total points for the user
        point.total_point += task.task_point  # Add task points to user's total points
        session.add(point)
        await session.commit()
        await session.refresh(point)

        return {
            "message": "Task completed and points added", 
            "points_received": task.task_point, 
            "new_total_points": point.total_point
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))