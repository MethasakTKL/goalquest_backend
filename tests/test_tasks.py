# from httpx import AsyncClient
# from goalquest_backend import models
# import pytest
# from datetime import datetime, timedelta

# @pytest.mark.asyncio
# async def test_no_permission_create_task(client: AsyncClient, goal_user1: models.Goal):
#     payload = {
#         "title": "Test Task",
#         "description": "Test Description Task",
#         "is_completed": False,
#         "task_point": 500,
#         "due_date": "2024-01-01T00:00:00",  # ใช้วันที่ในอนาคต
#         "goal_id": goal_user1.goal_id,
#     }

#     response = await client.post("/tasks/", json=payload)

#     assert response.status_code == 401  # คาดหวังว่า Unauthorized

# @pytest.mark.asyncio
# async def test_create_task(client: AsyncClient, token_user1: models.Token, goal_user1: models.Goal):
#     headers = {
#         "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
#     }
#     payload = {
#         "title": "Test Task",
#         "description": "Test Description Task",
#         "is_completed": False,
#         "task_point": 500,
#         "due_date": "2024-01-01T00:00:00",
#         "goal_id": goal_user1.goal_id,
#     }

#     response = await client.post("/tasks/", json=payload, headers=headers)
#     data = response.json()

#     assert response.status_code == 201  # คาดหวังว่า Created
#     assert "task_id" in data
#     assert data["title"] == payload["title"]
#     assert data["description"] == payload["description"]
#     assert data["is_completed"] == payload["is_completed"]
#     assert data["task_point"] == payload["task_point"]
#     assert data["goal_id"] == payload["goal_id"]

# @pytest.mark.asyncio
# async def test_no_permission_read_task(client: AsyncClient, task_user1: models.Task):
#     response = await client.get(f"/tasks/{task_user1.task_id}")

#     assert response.status_code == 401  # คาดหวังว่า Unauthorized

# @pytest.mark.asyncio
# async def test_read_task(client: AsyncClient, token_user1: models.Token, task_user1: models.Task):
#     headers = {
#         "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
#     }
#     response = await client.get(f"/tasks/{task_user1.task_id}", headers=headers)
#     data = response.json()

#     assert response.status_code == 200  # คาดหวังว่า OK
#     assert data["task_id"] == task_user1.task_id
#     assert data["title"] == task_user1.title

# @pytest.mark.asyncio
# async def test_no_permission_update_task(client: AsyncClient, task_user1: models.Task):
#     payload = {
#         "title": "Updated Task Title",
#         "description": "Updated Description",
#         "is_completed": True,
#         "task_point": 600,
#         "due_date": "2024-01-02T00:00:00",
#         "goal_id": task_user1.goal_id,  # ตรวจสอบให้แน่ใจว่า goal_id รวมอยู่ด้วย
#     }

#     response = await client.put(f"/tasks/{task_user1.task_id}", json=payload)
#     assert response.status_code == 401  # คาดหวังว่า Unauthorized

# @pytest.mark.asyncio
# async def test_update_task(client: AsyncClient, token_user1: models.Token, task_user1: models.Task):
#     headers = {
#         "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
#     }
#     payload = {
#         "title": "Updated Task Title",
#         "description": "Updated Description",
#         "is_completed": True,
#         "task_point": 600,
#         "due_date": "2024-01-02T00:00:00",
#         "goal_id": task_user1.goal_id,  # ตรวจสอบให้แน่ใจว่า goal_id รวมอยู่ด้วย
#     }

#     response = await client.put(f"/tasks/{task_user1.task_id}", json=payload, headers=headers)
#     data = response.json()

#     assert response.status_code == 200  # คาดหวังว่า OK
#     assert data["task_id"] == task_user1.task_id
#     assert data["title"] == payload["title"]
#     assert data["is_completed"] == payload["is_completed"]

# @pytest.mark.asyncio
# async def test_no_permission_delete_task(client: AsyncClient, task_user1: models.Task):
#     response = await client.delete(f"/tasks/{task_user1.task_id}")
#     assert response.status_code == 401  # คาดหวังว่า Unauthorized

# @pytest.mark.asyncio
# async def test_delete_task(client: AsyncClient, token_user1: models.Token, task_user1: models.Task):
#     headers = {
#         "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
#     }
#     response = await client.delete(f"/tasks/{task_user1.task_id}", headers=headers)

#     assert response.status_code == 200  # คาดหวังว่า OK
#     assert response.json() == {"detail": "Task deleted"}

# @pytest.mark.asyncio
# async def test_read_all_tasks(client: AsyncClient, token_user1: models.Token, task_user1: models.Task):
#     headers = {
#         "Authorization": f"{token_user1.token_type} {token_user1.access_token}"
#     }
#     response = await client.get("/tasks/all_task", headers=headers)
#     data = response.json()

#     assert response.status_code == 200  # คาดหวังว่า OK
#     assert isinstance(data, list)
#     assert any(task["task_id"] == task_user1.task_id for task in data)  # ตรวจสอบให้แน่ใจว่างานนั้นอยู่ในรายการ
