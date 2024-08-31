from httpx import AsyncClient
from goalquest_backend import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_read_points(
    client: AsyncClient,
):
    response = await client.get(f"/points/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_permissioned_read_points(
    client: AsyncClient,
    token_user1: models.Token,  # ใช้ Token ของ user1 ที่มีสิทธิ์
    example_point_user1: models.Point,  # ใช้ Point ที่สร้างจาก fixture
):
    headers = {
        "Authorization": f"Bearer {token_user1.access_token}",
    }
    
    response = await client.get(f"/points/", headers=headers)

    assert response.status_code == 200
    point_data = response.json()
    assert point_data["user_id"] == token_user1.user_id
    assert "total_point" in point_data
    assert "last_earned_at" in point_data
    assert point_data["total_point"] == 10000
