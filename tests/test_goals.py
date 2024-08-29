from httpx import AsyncClient
from goalquest_backend import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_goal(
    client: AsyncClient,
    user1 : models.DBUser,
):
    payload = {
        "title": "Test Goal",
        "description": "Test Description",
        "progress": 0,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
    }

    response = await client.post("/goals/", json=payload)

    assert response.status_code == 401