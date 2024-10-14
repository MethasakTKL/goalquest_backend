# from httpx import AsyncClient
# from goalquest_backend import models
# from goalquest_backend.models import Point, Task
# from sqlalchemy.ext.asyncio import AsyncSession
# import pytest

# @pytest.mark.asyncio
# async def test_complete_task(
#     client: AsyncClient,
#     token_user1: models.Token,
#     task_user1: Task,
#     example_point_user1: Point,
#     session: AsyncSession
# ):
#     initial_points = example_point_user1.total_point

#     response = await client.post(
#         "/actions_task/",
#         params={"task_id": task_user1.task_id},
#         headers={"Authorization": f"Bearer {token_user1.access_token}"}
#     )

#     assert response.status_code == 200
#     data = response.json()
#     assert data["message"] == "Task completed and points added"
#     assert data["points_received"] == task_user1.task_point

#     # อัปเดตข้อมูลของ Point ในฐานข้อมูล
#     await session.refresh(example_point_user1)

#     # คำนวณจำนวน point ที่จะได้รับจากการทำ task
#     expected_points = initial_points + task_user1.task_point

#     # ตรวจสอบว่า point ถูกเพิ่มขึ้นมาเป็นจำนวนที่ถูกต้อง
#     assert example_point_user1.total_point == expected_points, \
#         f"Expected points: {expected_points}, but got: {example_point_user1.total_point}"

#     # ตรวจสอบว่า task ถูกทำเสร็จแล้ว
#     await session.refresh(task_user1)
#     assert task_user1.is_completed, f"Task with ID {task_user1.task_id} should be marked as completed"


