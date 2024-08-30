from httpx import AsyncClient
from goalquest_backend import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_task(
    client: AsyncClient,
    goal_user1: models.Goal,
):
    payload = {
        "title": "Test Task",
        "description": "Test Description Task",
        "is_completed": False,
        "task_point": 500,
        "due_date": "2023-01-01T00:00:00",
        "goal_id": goal_user1.goal_id,
    }

    response = await client.post("/tasks/", json=payload)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_task(
    client: AsyncClient,
    token_user1: models.Token,
    goal_user1: models.Goal,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }
    payload = {
        "title": "Test Task",
        "description": "Test Description Task",
        "is_completed": False,
        "task_point": 500,
        "due_date": "2023-01-01T00:00:00",
        "goal_id": goal_user1.goal_id,
    }

    response = await client.post("/tasks/", json=payload, headers=headers)
    data = response.json()

    print("Create Task Status Code:", response.status_code)
    print("Create Task Response:", data)
     
    assert response.status_code == 200
    assert "task_id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["is_completed"] == payload["is_completed"]
    assert data["task_point"] == payload["task_point"]
    assert data["due_date"] == payload["due_date"]
    assert data["goal_id"] == payload["goal_id"]

@pytest.mark.asyncio
async def test_no_permission_read_tasks(
    client: AsyncClient,
    task_user1: models.Task,
):
    response = await client.get(f"/tasks/{task_user1.task_id}")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_tasks(
    client: AsyncClient,
    token_user1: models.Token,
    task_user1: models.Task,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }
    response = await client.get(f"/tasks/{task_user1.task_id}", headers=headers)
    data = response.json()
    print("Read Tasks Status Code:", response.status_code)
    print("Read Tasks Response:", data)

    assert response.status_code == 200
    assert "task_id" in data
    assert data["task_id"] > 0

@pytest.mark.asyncio
async def test_no_permission_update_tasks(
    client: AsyncClient,
    goal_user1: models.Goal,
    task_user1: models.Task,
):
    payload = {
        "title": "Task 1",
        "description": "Test Description Task 1",
        "is_completed": False,
        "task_point": 1000,
        "due_date": "2023-01-01T00:00:00",
        "goal_id": goal_user1.goal_id,
    }

    response = await client.put(f"/tasks/{task_user1.task_id}", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_tasks(
    client: AsyncClient,
    token_user1: models.Token,
    goal_user1: models.Goal,
    task_user1: models.Task,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }

    payload = {
        "title": "Task 1",
        "description": "Test Description Task 1",
        "is_completed": False,
        "task_point": 1000,
        "due_date": "2023-01-01T00:00:00",
        "goal_id": goal_user1.goal_id,
    }

    response = await client.put(
        f"/tasks/{task_user1.task_id}", json=payload, headers=headers
    )
    data = response.json()
    print("Update Tasks Status Code:", response.status_code)
    print("Update Tasks Response:", data)

    assert response.status_code == 200
    assert "task_id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["is_completed"] == payload["is_completed"]
    assert data["task_point"] == payload["task_point"]
    assert data["due_date"] == payload["due_date"]
    assert data["goal_id"] == payload["goal_id"]

@pytest.mark.asyncio
async def test_no_permission_delete_tasks(
    client: AsyncClient,
    task_user1: models.Task,
):
    response = await client.delete(f"/tasks/{task_user1.task_id}")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_goals(
    client: AsyncClient,
    token_user1: models.Token,
    task_user1: models.Task,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }

    response = await client.delete(f"/tasks/{task_user1.task_id}", headers=headers)
    data = response.json()
    print("Delete Tasks Status Code:", response.status_code)
    print("Delete Tasks Response:", data)

    assert response.status_code == 200