from typing import List
from pydantic import BaseModel, Field
import pydantic
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
import datetime

class BaseGoal(BaseModel):
    title: str = pydantic.Field(json_schema_extra=dict(example="Goal Title"))
    description: str = pydantic.Field(json_schema_extra=dict(example="Description of the goal"))
    progress_percentage: float = pydantic.Field(json_schema_extra=dict(example=0.0))
    start_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)
    end_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)
    is_complete: bool = pydantic.Field(json_schema_extra=dict(example=False))

class Goal(BaseGoal, SQLModel, table=True):
    __tablename__ = "goals"
    
    goal_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    start_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)
    end_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)
    created_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,  
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )
    is_complete: bool = pydantic.Field(default=False)
    