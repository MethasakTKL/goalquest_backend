from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from goalquest_backend.models import get_session
from goalquest_backend.models.users import DBUser, RegisteredUser,ChangedPassword,DeleteUserRequest
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Create User
@router.post("/")
async def create_user(user: RegisteredUser, session: AsyncSession = Depends(get_session)):
    query = select(DBUser).where(DBUser.username == user.username)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = DBUser(**user.dict())
    await db_user.set_password(user.password)  # Encrypt password before saving
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

# Read User
@router.get("/{user_id}")
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update User
@router.put("/edit-profile/{user_id}")
async def update_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if username:
        user.username = username
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:
        user.email = email

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Change Password
@router.put("/change-password/{user_id}")
async def change_password(
    user_id: int,
    request: ChangedPassword,
    session: AsyncSession = Depends(get_session)
):
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not await user.verify_password(request.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    await user.set_password(request.new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "Password updated successfully"}

# Delete User
@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    request: DeleteUserRequest,
    session: AsyncSession = Depends(get_session)
):
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not await user.verify_password(request.password):
        raise HTTPException(status_code=400, detail="Password is incorrect")

    await session.delete(user)
    await session.commit()
    return {"message": "User deleted successfully"}