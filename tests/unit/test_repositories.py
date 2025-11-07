# tests/unit/test_repositories.py

import pytest
from app.db.repositories.project import project_repository
from app.db.repositories.blog import blog_repository
from app.models.project import Project
from app.models.blog import BlogPost


class TestProjectRepository:
    
    @pytest.mark.asyncio
    async def test_create_project(self, test_db):
        from app.schemas.project import ProjectCreate
        
        project_data = ProjectCreate(
            title="New Project",
            description="Project description",
            technologies="Python, FastAPI",
            featured=False
        )
        
        project = await project_repository.create(test_db, obj_in=project_data)
        
        assert project.id is not None
        assert project.title == "New Project"
        assert project.featured is False
    
    @pytest.mark.asyncio
    async def test_get_project(self, test_db, test_project):
        project = await project_repository.get(test_db, test_project.id)
        
        assert project is not None
        assert project.id == test_project.id
        assert project.title == test_project.title
    
    @pytest.mark.asyncio
    async def test_get_featured_projects(self, test_db, test_project):
        projects = await project_repository.get_featured(test_db)
        
        assert len(projects) > 0
        assert all(p.featured for p in projects)
    
    @pytest.mark.asyncio
    async def test_update_project(self, test_db, test_project):
        from app.schemas.project import ProjectUpdate
        
        update_data = ProjectUpdate(title="Updated Title")
        updated_project = await project_repository.update(
            test_db,
            db_obj=test_project,
            obj_in=update_data
        )
        
        assert updated_project.title == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_delete_project(self, test_db, test_project):
        result = await project_repository.delete(test_db, id=test_project.id)
        
        assert result is True
        
        deleted_project = await project_repository.get(test_db, test_project.id)
        assert deleted_project is None


class TestBlogRepository:
    
    @pytest.mark.asyncio
    async def test_create_blog_post(self, test_db):
        from app.schemas.blog import BlogPostCreate
        
        post_data = BlogPostCreate(
            title="New Post",
            slug="new-post",
            content="Post content",
            author="Test Author",
            published=True
        )
        
        post = await blog_repository.create(test_db, obj_in=post_data)
        
        assert post.id is not None
        assert post.title == "New Post"
        assert post.slug == "new-post"
    
    @pytest.mark.asyncio
    async def test_get_by_slug(self, test_db, test_blog_post):
        post = await blog_repository.get_by_slug(test_db, test_blog_post.slug)
        
        assert post is not None
        assert post.id == test_blog_post.id
        assert post.slug == test_blog_post.slug
    
    @pytest.mark.asyncio
    async def test_get_published_posts(self, test_db, test_blog_post):
        posts = await blog_repository.get_published(test_db)
        
        assert len(posts) > 0
        assert all(p.published for p in posts)
    
    @pytest.mark.asyncio
    async def test_increment_views(self, test_db, test_blog_post):
        initial_views = test_blog_post.views
        
        await blog_repository.increment_views(test_db, test_blog_post.id)
        
        await test_db.refresh(test_blog_post)
        assert test_blog_post.views == initial_views + 1