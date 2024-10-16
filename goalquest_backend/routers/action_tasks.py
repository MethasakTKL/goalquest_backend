from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point
from goalquest_backend.models.tasks import Task
from goalquest_backend.models.earn_history import EarnHistory
from goalquest_backend.models.goals import Goal
from typing import Annotated
from datetime import datetime, timedelta

from .. import deps
from .. import models

router = APIRouter(
    prefix="/action_task",
    tags=["Complete Task  [Transaction]"]
)

@router.post("/complete/")
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

        earn_history = EarnHistory(
            user_id = current_user.id,
            task_id = task.task_id,
            points_earned =  task.task_point,
            earn_date = datetime.now(),
        )
        session.add(earn_history)
        await session.commit()

        return {
            "message": "Task completed and points added", 
            "points_received": task.task_point, 
            "new_total_points": point.total_point
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/click_task/")
async def click_task(
        task_id: int,
        session: Annotated[AsyncSession, Depends(get_session)],
        current_user: Annotated[models.User, Depends(deps.get_current_user)],
        last_action: datetime = None
):
        try:
            # Fetch the task from the database
            task = await session.get(Task, task_id)
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")

            # กำหนดค่า last_action ถ้าไม่ได้ส่งมา
            last_action = last_action or datetime.now()

            # ตรวจสอบว่า task ทำในวันเดียวกันแล้วหรือไม่
            is_same_day = (
                task.last_action is not None and
                task.last_action.year == last_action.year and
                task.last_action.month == last_action.month and
                task.last_action.day == last_action.day
            )

            # ถ้าไม่ใช่วันเดียวกัน ให้คำนวณ nextAction ใหม่
            next_action = task.next_action
            if not is_same_day and task.repeat_day is not None:
                next_action = last_action + timedelta(days=task.repeat_day)

            # Update task fields and save back to the database
            task.last_action = last_action
            task.next_action = next_action
            task.task_count += 1  # เพิ่ม task_count เมื่อทำ action

            # คำนวณความต่างระหว่าง start_date และ due_date
            duration = task.due_date - task.start_date
            total_days = duration.days

            # คำนวณ repeatCount
            repeat_count = total_days // task.repeat_day if task.repeat_day else 1

            # ตรวจสอบว่าถ้า task_count >= repeat_count ให้ถือว่า task เสร็จแล้ว
            if task.task_count >= repeat_count:
                task.is_completed = True
                task.next_action = None  # ไม่ต้องคำนวณ next_action ถ้า task เสร็จแล้ว

            # Save the updated task to the database
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "message": "Task updated successfully",
                "task": task
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
        
@router.post("/give_up_task/")
async def give_up_task(
        task_id: int,
        session: Annotated[AsyncSession, Depends(get_session)],
        current_user: Annotated[models.User, Depends(deps.get_current_user)]
):
    try:
        # Fetch the task from the database
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        # Fetch the associated goal to check user ownership
        goal = await session.get(Goal, task.goal_id)
        if goal is None:
            raise HTTPException(status_code=404, detail="Goal not found")

        # ตรวจสอบว่า goal นี้เป็นของผู้ใช้คนนี้หรือไม่
        if goal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to give up this task")

        # Set คะแนน task ให้เหลือ 30 และทำให้ task เสร็จสิ้นจากการยอมแพ้
        task.task_point = 30
        task.is_completed = True

        # Fetch user's points
        points = await session.execute(select(Point).where(Point.user_id == current_user.id))
        points = points.scalar_one_or_none()

        if points is None:
            raise HTTPException(status_code=404, detail="User points not found")

        # หักคะแนนออก 30 คะแนนจากคะแนนรวม
        points.total_point -= 30

        # ไม่ให้คะแนนติดลบ
        if points.total_point < 0:
            points.total_point = 0

        # Save the task and user's points
        session.add(task)
        session.add(points)
        await session.commit()
        await session.refresh(task)

        return {
            "message": "You gave up the task",
            "task": task,
            "remaining_points": points.total_point
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")