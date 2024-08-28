from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.tasks import Task

router = APIRouter(
    prefix="/done_task",
    tags=["Done Task  [Transaction]"]
)

@router.post("/")
async def complete_task(user_id: int, task_id: int, session: AsyncSession = Depends(get_session)):
    # Fetch point data for the user
    point = await session.execute(select(Point).where(Point.user_id == user_id))
    point = point.scalar_one_or_none()

    if point is None:
        raise HTTPException(status_code=404, detail="Points not found for the given user")

    # Fetch task data
    task = await session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task is already completed
    if task.is_completed:
        return {"message": "Task is already completed, no additional points awarded"}

    # Mark the task as completed and add points
    task.is_completed = True
    point.total_point += task.task_point
    await session.commit()

    return {"message": "Task completed and points added", "points_received": point.total_point}