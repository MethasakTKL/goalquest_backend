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
    is_completed: bool = Field(default = False)
    task_point: int = pydantic.Field(json_schema_extra=dict(example=500)) 
    due_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)


class Task(BaseTask, SQLModel, table=True):
    __tablename__ = "tasks"

    task_id: int = Field(default=None, primary_key=True)
    goal_id: int = Field(default=None, foreign_key="goals.goal_id")
    created_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,  
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )


    