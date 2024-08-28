from pydantic import BaseModel, Field
import pydantic
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
from typing import Optional
import datetime

class BasePoint(BaseModel):
    user_id: int = pydantic.Field(json_schema_extra=dict(example=0)) 
    total_point: int = pydantic.Field(json_schema_extra=dict(example=0)) 
    last_earned_at: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )


class Point(BasePoint, SQLModel, table=True):
    __tablename__ = "points"
    
    point_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    total_point: int
    last_earned_at: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
