# tests/integration/test_projects_api.py

import pytest
from httpx import AsyncClient


class TestProjectsAPI:
    
    @pytest.mark.asyncio
    async def test_get_projects(self, client: AsyncClient, test_project):
        response = await client.get("/api/v1/projects/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_get_project_by_id(self, client: AsyncClient, test_project):
        response = await client.get(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
        assert data["title"] == test_project.title
    
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, admin_headers):
        response = await client.post(
            "/api/v1/projects/",
            headers=admin_headers,
            json={
                "title": "New API Project",
                "description": "Created via API",
                "technologies": "Python, FastAPI",
                "featured": False
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New API Project"
    
    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient, admin_headers, test_project):
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            headers=admin_headers,
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient, admin_headers, test_project):
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204


class TestProjectComments:
    
    @pytest.mark.asyncio
    async def test_add_comment(self, client: AsyncClient, test_project, mock_email_service):
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/comments",
            json={
                "name": "Test Commenter",
                "email": "commenter@example.com",
                "content": "Great project!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Commenter"
        assert data["approved"] is False