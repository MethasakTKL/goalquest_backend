from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.tasks import BaseTask, Task , TaskwithId
from goalquest_backend.models.goals import Goal
from goalquest_backend.models.users import DBUser 
from datetime import datetime
from typing import Annotated, List

from .. import deps

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=Task)
async def create_task(
    task: BaseTask,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[DBUser, Depends(deps.get_current_user)]
) -> Task:
    # ตรวจสอบว่า goal มีอยู่และเป็นของผู้ใช้ปัจจุบัน
    goal = await session.get(Goal, task.goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create tasks for this goal")
    
    # ตรวจสอบ task_type และตั้งค่า repeat_day หรือ task_duration ตามเงื่อนไข
    if task.task_type == 'FocusTimer':
        task.repeat_day = None  # ถ้า task_type เป็น FocusTimer, repeat_day ต้องเป็น null
    elif task.task_type == 'TodoQuest':
        task.task_duration = None  # ถ้า task_type เป็น TodoQuest, task_duration ต้องเป็น null
    
    # แปลงเวลาทั้งหมดให้เป็น offset-naive (ไม่มี timezone)
    if task.start_date:
        task.start_date = task.start_date.replace(tzinfo=None)
    if task.due_date:
        task.due_date = task.due_date.replace(tzinfo=None)

    task.is_completed = False

    # ตั้งค่าเริ่มต้นให้ last_action เป็น None
    task.last_action = None

    # ตั้งค่า next_action ให้เท่ากับ start_date
    task.next_action = task.start_date

    # สร้าง Task ใหม่และบันทึกลงฐานข้อมูล
    db_task = Task(**task.dict())
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@router.get("/all_task", response_model=List[TaskwithId])
async def read_all_tasks(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[DBUser, Depends(deps.get_current_user)]
) -> List[TaskwithId]:
    # Fetch tasks for the current user
    tasks = await session.execute(select(Task).join(Goal).where(Goal.user_id == current_user.id))
    task_list = tasks.scalars().all()
    return task_list

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[DBUser, Depends(deps.get_current_user)]
) -> Task:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    goal = await session.get(Goal, task.goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: BaseTask,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[DBUser, Depends(deps.get_current_user)]
) -> Task:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    goal = await session.get(Goal, task.goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    task.title = task_update.title
    task.description = task_update.description
    task.due_date = task_update.due_date
    task.task_point = task_update.task_point
    task.is_completed = task_update.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[DBUser, Depends(deps.get_current_user)]
) -> dict:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    goal = await session.get(Goal, task.goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    await session.delete(task)
    await session.commit()
    return {"detail": "Task deleted"}