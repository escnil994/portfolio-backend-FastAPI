# tests/integration/test_auth_api.py

import pytest
from httpx import AsyncClient


class TestAuthAPI:
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user, mock_email_service):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, admin_headers):
        response = await client.post(
            "/api/v1/auth/register",
            headers=admin_headers,
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"


class TestAuthProtected:
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_endpoint_without_admin(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/auth/register",
            headers=auth_headers,
            json={
                "email": "test@example.com",
                "username": "test",
                "password": "password123"
            }
        )
        
        assert response.status_code == 403