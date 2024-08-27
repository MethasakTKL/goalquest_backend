from pydantic import BaseModel, Field
from typing import Optional
from sqlmodel import SQLModel, Field 
import pydantic
import datetime


class BaseReward(BaseModel):
    title: str = pydantic.Field(json_schema_extra=dict(example="Reward Title"))
    description: str = pydantic.Field(json_schema_extra=dict(example="Description of the reward")) 
    points_required: int = pydantic.Field(json_schema_extra=dict(example=500))


class Reward(BaseReward, SQLModel, table=True):
    __tablename__ = "rewards"
    
    reward_id: int = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)