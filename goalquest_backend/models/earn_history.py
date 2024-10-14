from pydantic import BaseModel, Field
import pydantic
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
from datetime import datetime

class BaseEarnHistory(BaseModel):
    user_id: int = pydantic.Field(0, example=0)
    task_id: int = pydantic.Field(0, example=0)
    points_earned: int = Field(default=0)
    earn_date: datetime = Field(default_factory=datetime.utcnow)

class EarnHistory(BaseEarnHistory, SQLModel, table=True):
    __tablename__ = "earn_points"
    
    earn_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    task_id: int = Field(default=None, foreign_key="tasks.task_id")