from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.users import DBUser, RegisteredUser

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/")
async def create_user(user: RegisteredUser, session: AsyncSession = Depends(get_session)):
    query = select(DBUser).where(DBUser.username == user.username)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = DBUser(**user.dict())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/{user_id}")
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user