from pydantic import BaseModel, Field
import pydantic
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
import datetime

class BaseRewardHistory(BaseModel):
    user_id: int = pydantic.Field(json_schema_extra=dict(example=0))
    reward_id: int = pydantic.Field(json_schema_extra=dict(example=0))
    points_spent: int = pydantic.Field(json_schema_extra=dict(example=1500))
    redeemed_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)

class RewardHistory(BaseRewardHistory, SQLModel, table=True):
    __tablename__ = "reward_history"
    
    history_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    reward_id: int = Field(default=None, foreign_key="rewards.reward_id")
    points_spent: int
    redeemed_date: datetime.datetime = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None)