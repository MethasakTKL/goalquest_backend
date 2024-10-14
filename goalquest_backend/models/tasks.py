from pydantic import BaseModel, Field
import pydantic
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
from typing import Optional
import datetime

class BaseTask(BaseModel):
    goal_id: int = pydantic.Field(json_schema_extra=dict(example=0)) 
    title: str = pydantic.Field(json_schema_extra=dict(example="Task Title"))
    description: str = pydantic.Field(json_schema_extra=dict(example="Description of the task"))
    task_type: str = pydantic.Field(json_schema_extra=dict(example="Task Type"))
    is_completed: bool = Field(default = False)
    repeat_day: Optional[int] = Field(None)  
    task_duration: Optional[int] = Field(None)
    task_count: int = Field(default=0)
    task_point: int = pydantic.Field(default=500, json_schema_extra=dict(example=500))  # กำหนดค่าเริ่มต้นเป็น 500
    start_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None) 
    due_date: Optional[datetime.datetime] = pydantic.Field(  # แก้ไขให้ Optional
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)
    last_action: Optional[datetime.datetime] = Field(default=None)  # วันสุดท้ายที่ action ถูกทำ
    next_action: Optional[datetime.datetime] = Field(default=None)  # วันถัดไปที่ task จะถูกทำ
    
class TaskwithId(BaseTask):
    task_id: int 
    
class Task(BaseTask, SQLModel, table=True):
    __tablename__ = "tasks"

    task_id: int = Field(default=None, primary_key=True)
    goal_id: int = Field(default=None, foreign_key="goals.goal_id", ondelete="CASCADE")
    task_type: str = Field(nullable=False)
    created_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,  
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )



    # def calculate_next_action(self):
    #     if self.repeat_day and self.last_action:
    #         self.next_action = self.last_action + datetime.timedelta(days=self.repeat_day)
    #     elif self.repeat_day and not self.last_action:
    #         self.next_action = self.created_at + datetime.timedelta(days=self.repeat_day)
    #     else:
    #         self.next_action = None


    