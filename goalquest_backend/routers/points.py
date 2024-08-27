from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point, BasePoint
from goalquest_backend.models.users import DBUser

router = APIRouter(
    prefix="/points",
    tags=["points"]
)

@router.post("/", response_model=Point)
async def create_point(point: BasePoint, session: AsyncSession = Depends(get_session)):
    user = await session.get(DBUser, point.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_point = Point(**point.dict())
    session.add(db_point)
    await session.commit()
    await session.refresh(db_point)
    return db_point

@router.get("/{point_id}", response_model=Point)
async def read_point(point_id: int, session: AsyncSession = Depends(get_session)):
    point = await session.get(Point, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    return point

@router.put("/{point_id}", response_model=Point)
async def update_point(point_id: int, point_update: BasePoint, session: AsyncSession = Depends(get_session)):
    point = await session.get(Point, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")

    point.total_point = point_update.total_point
    point.last_earned_at = point_update.last_earned_at

    session.add(point)
    await session.commit()
    await session.refresh(point)
    return point

@router.delete("/{point_id}", response_model=dict)
async def delete_point(point_id: int, session: AsyncSession = Depends(get_session)):
    point = await session.get(Point, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")

    await session.delete(point)
    await session.commit()
    return {"detail": "Point deleted"}