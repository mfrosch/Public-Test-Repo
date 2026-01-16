"""
Tests for Authentication API endpoints.
"""
import pytest
from httpx import AsyncClient

from src.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestAuthEndpoints:
    """Test cases for authentication operations."""

    @pytest.mark.asyncio
    async def test_register_user(self, client):
        """Test user registration."""
        response = await client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Test registration with existing email fails."""
        # Register first user
        await client.post("/api/auth/register", json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "SecurePass123!",
        })

        # Try to register with same email
        response = await client.post("/api/auth/register", json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "SecurePass123!",
        })

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        """Test registration with existing username fails."""
        # Register first user
        await client.post("/api/auth/register", json={
            "email": "user1@example.com",
            "username": "sameusername",
            "password": "SecurePass123!",
        })

        # Try to register with same username
        response = await client.post("/api/auth/register", json={
            "email": "user2@example.com",
            "username": "sameusername",
            "password": "SecurePass123!",
        })

        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Test successful login."""
        # Register user
        await client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "SecurePass123!",
        })

        # Login
        response = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123!",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        """Test login with wrong password fails."""
        # Register user
        await client.post("/api/auth/register", json={
            "email": "wrongpass@example.com",
            "username": "wrongpassuser",
            "password": "SecurePass123!",
        })

        # Login with wrong password
        response = await client.post("/api/auth/login", json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword!",
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = await client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePassword123!",
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client):
        """Test getting current user info."""
        # Register and login
        await client.post("/api/auth/register", json={
            "email": "me@example.com",
            "username": "meuser",
            "password": "SecurePass123!",
        })

        login_response = await client.post("/api/auth/login", json={
            "email": "me@example.com",
            "password": "SecurePass123!",
        })

        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["username"] == "meuser"

    @pytest.mark.asyncio
    async def test_refresh_token(self, client):
        """Test token refresh."""
        # Register and login
        await client.post("/api/auth/register", json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "SecurePass123!",
        })

        login_response = await client.post("/api/auth/login", json={
            "email": "refresh@example.com",
            "password": "SecurePass123!",
        })

        token = login_response.json()["access_token"]

        # Refresh token
        response = await client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        # New token should be different
        assert data["access_token"] != token

    @pytest.mark.asyncio
    async def test_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
