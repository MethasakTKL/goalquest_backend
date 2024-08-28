from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.tasks import Task

router = APIRouter(
    prefix="/done_task",
    tags=["Done Task"]
)

@router.post("/")
async def complete_task(task_id: int, point_id:int , session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    point = await session.get(Point, point_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.is_completed == True:
        point.total_point += task.task_point
        await session.commit()
        return {"message": "Task completed and points added" , "points_recive": point.total_point}
    else:
        return {"message": "Task is not completed"}