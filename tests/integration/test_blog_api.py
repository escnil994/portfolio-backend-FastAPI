# tests/integration/test_blog_api.py

import pytest
from httpx import AsyncClient


class TestBlogAPI:
    
    @pytest.mark.asyncio
    async def test_get_blog_posts(self, client: AsyncClient, test_blog_post):
        response = await client.get("/api/v1/blog/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_get_blog_post_by_slug(self, client: AsyncClient, test_blog_post):
        response = await client.get(f"/api/v1/blog/{test_blog_post.slug}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_blog_post.slug
        assert data["title"] == test_blog_post.title
    
    @pytest.mark.asyncio
    async def test_create_blog_post(self, client: AsyncClient, admin_headers):
        response = await client.post(
            "/api/v1/blog/",
            headers=admin_headers,
            json={
                "title": "New Blog Post",
                "slug": "new-blog-post",
                "content": "Post content",
                "author": "Test Author",
                "published": True
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Blog Post"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_slug(self, client: AsyncClient, admin_headers, test_blog_post):
        response = await client.post(
            "/api/v1/blog/",
            headers=admin_headers,
            json={
                "title": "Another Post",
                "slug": test_blog_post.slug,
                "content": "Content",
                "author": "Author",
                "published": True
            }
        )
        
        assert response.status_code == 400