from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.points import Point, BasePoint
from goalquest_backend.models.users import DBUser
from typing import Annotated

from .. import deps
from .. import models

router = APIRouter(
    prefix="/points",
    tags=["Points"]
)

# @router.post("/", response_model=Point)
# async def create_point(point: BasePoint, session: AsyncSession = Depends(get_session)):
#     user = await session.get(DBUser, point.user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     db_point = Point(**point.dict())
#     session.add(db_point)
#     await session.commit()
#     await session.refresh(db_point)
#     return db_point

@router.get("/", response_model=Point)
async def read_point(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    ) -> Point:
    
    result = await session.execute(select(Point).where(Point.user_id == current_user.id))
    point = result.scalars().first()

    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    if point.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this point")
    
    return point
from typing import List

from typing import List

@router.get("/all", response_model=List[Point])
async def read_all_points(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> List[Point]:
    # ดึง point ของผู้ใช้งานทั้งหมดจากฐานข้อมูล
    result = await session.execute(select(Point))
    points = result.scalars().all()

    if not points:
        raise HTTPException(status_code=404, detail="No points found")

    return points


# @router.put("/{point_id}", response_model=Point)
# async def update_point(point_id: int, point_update: BasePoint, session: AsyncSession = Depends(get_session)):
#     point = await session.get(Point, point_id)
#     if not point:
#         raise HTTPException(status_code=404, detail="Point not found")

#     point.total_point = point_update.total_point
#     point.last_earned_at = point_update.last_earned_at

#     session.add(point)
#     await session.commit()
#     await session.refresh(point)
#     return point

# @router.delete("/{point_id}", response_model=dict)
# async def delete_point(point_id: int, session: AsyncSession = Depends(get_session)):
#     point = await session.get(Point, point_id)
#     if not point:
#         raise HTTPException(status_code=404, detail="Point not found")

#     await session.delete(point)
#     await session.commit()
#     return {"detail": "Point deleted"}