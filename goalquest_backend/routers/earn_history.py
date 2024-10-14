from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.earn_history import EarnHistory
from sqlalchemy import desc

from .. import deps
from .. import models

router = APIRouter(
    prefix="/earn_history",
    tags=["Earn points History"]
)

@router.get("/")
async def get_earn_history(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
):
    try:
        # ดึงข้อมูลประวัติการได้รับคะแนนของผู้ใช้คนนี้
        result = await session.execute(
            select(EarnHistory).where(EarnHistory.user_id == current_user.id).order_by(desc(EarnHistory.earn_date))
        )
        earn_history = result.scalars().all()

        return earn_history

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))