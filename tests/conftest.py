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


import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)

@pytest.fixture(name = "app", scope = "session")
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
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(name = "user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )

    user = query.one_or_none()
    if user:
        return user
    
    user = models.DBUser(
        username = username,
        password = password,
        email = "user1@gmail.com",
        first_name = "Firstname1",
        last_name = "Lastname1",
        last_login_date = datetime.datetime.now(tz=datetime.timezone.utc),
    )

    await user.set_password(password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest_asyncio.fixture(name = "token_user1")
async def oauth_token_user1(user1: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return models.Token(
        access_token= security.create_access_token(
            data={"sub": user1.id},
            expires_delta = access_token_expires
        ),
        refresh_token= security.create_refresh_token(
            data = {"sub": user1.id},
            expires_delta = access_token_expires,
        ),
        token_type = "Bearer",
        scope="",
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at = datetime.datetime.now() + access_token_expires,
        issued_at = user1.last_login_date,
        user_id = user1.id
    )

@pytest_asyncio.fixture(name = "goal_user1")
async def example_goal_user1(
    session: models.AsyncSession, user1: models.DBUser 
) -> models.Goal:
    title = "Goal 1"

    query = await session.exec(
        models.select(models.Goal)
        .where(models.Goal.title == title, 
               models.Goal.user_id == user1.id)
        .limit(1)
    )

    goal = query.one_or_none()
    if goal:
        return goal
    
    goal = models.Goal(
        title = title,
        description = "Description 1",
        progress_percentage= 0,
        start_date = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        end_date = datetime.datetime(2023, 12, 31, tzinfo=datetime.timezone.utc),
        user_id = user1.id,
    )

    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal

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