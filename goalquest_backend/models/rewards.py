from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field
from typing import Optional
import datetime
import pydantic

class BaseReward(BaseModel):
    title: str = pydantic.Field(json_schema_extra=dict(example="Reward Title"))
    description: str = pydantic.Field(json_schema_extra=dict(example="Description of the reward")) 
    points_required: int = pydantic.Field(json_schema_extra=dict(example=500))
    is_redeemed: bool = pydantic.Field(json_schema_extra=dict(example=False))

class Reward(BaseReward, SQLModel, table=True):
    __tablename__ = "rewards"
    
    reward_id: int = Field(default=None, primary_key=True)
    created_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,  # Use default_factory to set current UTC time
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow,  # Use default_factory to set current UTC time
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )