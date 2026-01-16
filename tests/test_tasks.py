"""
Tests for Task API endpoints.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from src.main import app
from src.models.task import Priority, TaskStatus


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_headers(client):
    """Get authentication headers for test user."""
    # Register test user
    await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
    })

    # Login
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestTaskEndpoints:
    """Test cases for task CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_task(self, client, auth_headers):
        """Test creating a new task."""
        response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={
                "title": "Test Task",
                "description": "A test task description",
                "priority": "high",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, client, auth_headers):
        """Test creating a task with a due date."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

        response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={
                "title": "Task with deadline",
                "due_date": due_date,
            }
        )

        assert response.status_code == 201
        assert response.json()["due_date"] is not None

    @pytest.mark.asyncio
    async def test_list_tasks(self, client, auth_headers):
        """Test listing user tasks."""
        # Create some tasks first
        for i in range(3):
            await client.post(
                "/api/tasks/",
                headers=auth_headers,
                json={"title": f"Task {i}"}
            )

        response = await client.get("/api/tasks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_with_filter(self, client, auth_headers):
        """Test filtering tasks by status."""
        response = await client.get(
            "/api/tasks/",
            headers=auth_headers,
            params={"status": "pending"}
        )

        assert response.status_code == 200
        for task in response.json():
            assert task["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_task(self, client, auth_headers):
        """Test getting a single task."""
        # Create task
        create_response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={"title": "Get me"}
        )
        task_id = create_response.json()["id"]

        # Get task
        response = await client.get(
            f"/api/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Get me"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, client, auth_headers):
        """Test getting a task that doesn't exist."""
        response = await client.get(
            "/api/tasks/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, client, auth_headers):
        """Test updating a task."""
        # Create task
        create_response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={"title": "Original"}
        )
        task_id = create_response.json()["id"]

        # Update task
        response = await client.put(
            f"/api/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "Updated", "priority": "urgent"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_delete_task(self, client, auth_headers):
        """Test deleting a task."""
        # Create task
        create_response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={"title": "Delete me"}
        )
        task_id = create_response.json()["id"]

        # Delete task
        response = await client.delete(
            f"/api/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_task(self, client, auth_headers):
        """Test marking a task as complete."""
        # Create task
        create_response = await client.post(
            "/api/tasks/",
            headers=auth_headers,
            json={"title": "Complete me"}
        )
        task_id = create_response.json()["id"]

        # Complete task
        response = await client.post(
            f"/api/tasks/{task_id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Test that unauthenticated requests are rejected."""
        response = await client.get("/api/tasks/")
        assert response.status_code == 401
