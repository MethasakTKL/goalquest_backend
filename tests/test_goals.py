from httpx import AsyncClient
from goalquest_backend import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_goal(
    client: AsyncClient,
):
    payload = {
        "title": "Test Goal",
        "description": "Test Description",
        "progress_percentage": 0,
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T00:00:00",
    }

    response = await client.post("/goals/", json=payload)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_goal(
    client: AsyncClient,
    token_user1: models.Token,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }
    payload = {
        "title": "Test Goal",
        "description": "Test Description",
        "progress_percentage": 0,
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T00:00:00",
    }

    response = await client.post("/goals/", json=payload, headers=headers)
    data = response.json()

    print("Create Goal Status Code:", response.status_code)
    print("Create Goal Response:", data)

    assert response.status_code == 200
    assert "goal_id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["progress_percentage"] == payload["progress_percentage"]
    assert data["start_date"] == payload["start_date"]
    assert data["end_date"] == payload["end_date"]

@pytest.mark.asyncio
async def test_no_permission_read_goals(
    client: AsyncClient,
    goal_user1: models.Goal,
):
    response = await client.get(f"/goals/{goal_user1.goal_id}")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_goals(
    client: AsyncClient,
    token_user1: models.Token,
    goal_user1: models.Goal,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }
    response = await client.get(f"/goals/{goal_user1.goal_id}", headers=headers)
    data = response.json()
    print("Read Goals Status Code:", response.status_code)
    print("Read Goals Response:", data)

    assert response.status_code == 200
    assert "goal_id" in data
    assert data["goal_id"] > 0
    
@pytest.mark.asyncio
async def test_no_permission_update_goals(
    client: AsyncClient,
    goal_user1: models.Goal,
):
    payload = {
        "title": "Updated Goal",
        "description": "Updated Description",
        "progress_percentage": 50,
        "start_date": "2023-05-01T00:00:00",
        "end_date": "2023-10-31T00:00:00",
    }

    response = await client.put(f"/goals/{goal_user1.goal_id}", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_goals(
    client: AsyncClient,
    token_user1: models.Token,
    goal_user1: models.Goal,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }

    payload = {
        "title": "Updated Goal",
        "description": "Updated Description",
        "progress_percentage": 50,
        "start_date": "2023-05-01T00:00:00",
        "end_date": "2023-10-31T00:00:00",
    }

    response = await client.put(
        f"/goals/{goal_user1.goal_id}", json=payload, headers=headers
    )
    data = response.json()
    print("Update Goals Status Code:", response.status_code)
    print("Update Goals Response:", data)

    assert response.status_code == 200
    assert "goal_id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["progress_percentage"] == payload["progress_percentage"]
    assert data["start_date"] == payload["start_date"]
    assert data["end_date"] == payload["end_date"]

@pytest.mark.asyncio
async def test_no_permission_delete_goals(
    client: AsyncClient,
    goal_user1: models.Goal,
):
    response = await client.delete(f"/goals/{goal_user1.goal_id}")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_goals(
    client: AsyncClient,
    token_user1: models.Token,
    goal_user1: models.Goal,
):
    headers = {
        "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
    }

    response = await client.delete(f"/goals/{goal_user1.goal_id}", headers=headers)
    data = response.json()
    print("Delete Goals Status Code:", response.status_code)
    print("Delete Goals Response:", data)

    assert response.status_code == 200