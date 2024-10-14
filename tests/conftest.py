import asyncio
import pathlib
import datetime
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from typing import Any, Dict
from pydantic_settings import SettingsConfigDict
from goalquest_backend import config, models, main, security
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)

@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)
    asyncio.run(models.recreate_table())
    yield app

@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e

@pytest_asyncio.fixture(name="user1")
async def example_user1(session: AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    # Create the user in the database
    new_user = models.DBUser(
        username=username,
        email="user1@example.com",
        first_name="First",
        last_name="Last",
        password=password,
        register_date=datetime.utcnow(),  # Make sure this is correct
        updated_date=datetime.utcnow()     # Make sure this is correct
    )
    
    session.add(new_user)
    await session.commit()
    
    return new_user




@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Check for last_login_date
    issued_at = user1.last_login_date if user1.last_login_date else datetime.now(timezone.utc)
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user1.id},
            expires_delta=access_token_expires
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user1.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.now(datetime.timezone.utc) + access_token_expires,  # ใช้ timezone-aware
        issued_at=issued_at,  # ใช้ค่า issued_at ที่ตั้งไว้
        user_id=user1.id
    )

@pytest_asyncio.fixture(name="goal_user1")
async def example_goal_user1(session: AsyncSession, user1: models.DBUser) -> models.Goal:
    title = "Goal 1"

    query = await session.execute(
        models.select(models.Goal)
        .where(models.Goal.title == title, models.Goal.user_id == user1.id)
        .limit(1)
    )

    goal = query.scalar_one_or_none()
    if goal:
        return goal
    
    goal = models.Goal(
        title=title,
        description="First test goal",
        user_id=user1.id,
        start_date=datetime.now(tz=datetime.timezone.utc),
        due_date=datetime.now(tz=datetime.timezone.utc) + timedelta(days=30),  # แก้ไข
    )
    
    async with session.begin():  # ใช้ context manager
        session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal

@pytest_asyncio.fixture(name="task_user1")
async def example_task_user1(
    session: AsyncSession, user1: models.DBUser, goal_user1: models.Goal
) -> models.Task:
    title = "Task 1"

    query = await session.exec(
        models.select(models.Task)
        .where(models.Task.title == title, models.Task.goal_id == goal_user1.goal_id)
        .limit(1)
    )

    task = query.one_or_none()
    if task:
        return task
    
    task = models.Task(
        title=title,
        description="Description 1",
        is_completed=False,
        task_point=500,
        due_date=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        goal_id=goal_user1.goal_id,
    )

    async with session.begin():  # Use a context manager for the session
        session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@pytest_asyncio.fixture(name="example_point_user1")
async def example_point_user1(
    session: AsyncSession, user1: models.DBUser
) -> models.Point:
    query = await session.execute(
        models.select(models.Point).where(models.Point.user_id == user1.id).limit(1)
    )
    
    point = query.scalar_one_or_none()
    if point:
        return point
    
    point = models.Point(
        user_id=user1.id,
        total_point=10000,
        last_earned_at=datetime.datetime.utcnow()
    )

    async with session.begin():  # Use a context manager for the session
        session.add(point)
    await session.commit()
    await session.refresh(point)
    return point

@pytest_asyncio.fixture(name="example_reward1")
async def example_reward1_fixture(session: models.AsyncSession) -> models.Reward:
    reward = models.Reward(
        title="Test reward",
        description="Test reward description",
        points_required=100
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward)  
    return reward

@pytest_asyncio.fixture(name="example_reward2")
async def example_reward2_fixture(session: models.AsyncSession) -> models.Reward:
    reward = models.Reward(
        title="Another Test reward",
        description="Another Test reward description",
        points_required=200
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward)  
    return reward

@pytest_asyncio.fixture(name="example_reward3")
async def example_reward3_fixture(session: models.AsyncSession) -> models.Reward:
    reward = models.Reward(
        title="Third Test reward",
        description="Third Test reward description",
        points_required=300
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward)  
    return reward
