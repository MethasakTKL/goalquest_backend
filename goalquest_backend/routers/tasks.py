from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.tasks import BaseTask, Task
from goalquest_backend.models.goals import Goal
import datetime
from typing import List

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model = Task)
async def create_task(task: BaseTask, session: AsyncSession = Depends(get_session)):
    goal = await session.get(Goal, task.goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db_task = Task(**task.dict())
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@router.get("/all_task" , response_model=List[BaseTask])
async def read_all_tasks(session: AsyncSession = Depends(get_session)):
    task = await session.execute(select(Task))
    task_list = task.scalars().all()
    return task_list

@router.get("/{task_id}", response_model = Task)
async def read_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model = Task)
async def update_task(task_id : int, task_update : BaseTask,session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code = 404, detail = "Task not found")
    
    task.title = task_update.title
    task.description = task_update.description
    task.due_date = task_update.due_date
    task.task_point = task_update.task_point
    task.is_completed = task_update.is_completed
    task.updated_at = datetime.datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
    return {"detail": "Task deleted"}