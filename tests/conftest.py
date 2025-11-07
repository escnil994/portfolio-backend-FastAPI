# tests/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.config import settings
from app.services.auth import auth_service
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from app.models.blog import BlogPost


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    user = await auth_service.create_user(
        db=test_db,
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User",
        is_superuser=False
    )
    return user


@pytest.fixture
async def test_admin(test_db: AsyncSession) -> User:
    admin = await auth_service.create_user(
        db=test_db,
        email="admin@example.com",
        username="admin",
        password="adminpassword123",
        full_name="Admin User",
        is_superuser=True
    )
    return admin


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    access_token = auth_service.create_access_token(
        data={"user_id": test_user.id, "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_headers(test_admin: User) -> dict:
    access_token = auth_service.create_access_token(
        data={"user_id": test_admin.id, "email": test_admin.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_profile(test_db: AsyncSession) -> Profile:
    profile = Profile(
        username="johndoe",
        name="John",
        last_name="Doe",
        display_name="John Doe",
        title="Full Stack Developer",
        bio="Experienced developer",
        email="john@example.com",
        github_url="https://github.com/johndoe",
        linkedin_url="https://linkedin.com/in/johndoe",
        skills="Python, JavaScript, React"
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)
    return profile


@pytest.fixture
async def test_project(test_db: AsyncSession) -> Project:
    project = Project(
        title="Test Project",
        description="A test project description",
        content="Detailed content about the project",
        technologies="Python, FastAPI, SQLAlchemy",
        github_url="https://github.com/test/project",
        demo_url="https://demo.example.com",
        featured=True
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest.fixture
async def test_blog_post(test_db: AsyncSession) -> BlogPost:
    post = BlogPost(
        title="Test Blog Post",
        slug="test-blog-post",
        excerpt="This is a test excerpt",
        content="This is the full content of the test blog post",
        author="Test Author",
        tags="python, testing, fastapi",
        published=True,
        views=0
    )
    test_db.add(post)
    await test_db.commit()
    await test_db.refresh(post)
    return post


@pytest.fixture
def mock_email_service(monkeypatch):
    async def mock_send_contact_message(*args, **kwargs):
        return True
    
    async def mock_send_confirmation(*args, **kwargs):
        return True
    
    async def mock_send_comment_notification(*args, **kwargs):
        return True
    
    async def mock_send_2fa_code(*args, **kwargs):
        return True
    
    from app.services import email
    monkeypatch.setattr(
        email.email_service,
        "send_contact_message_notification",
        mock_send_contact_message
    )
    monkeypatch.setattr(
        email.email_service,
        "send_confirmation_to_user",
        mock_send_confirmation
    )
    monkeypatch.setattr(
        email.email_service,
        "send_comment_notification",
        mock_send_comment_notification
    )
    monkeypatch.setattr(
        email.email_service,
        "send_2fa_code",
        mock_send_2fa_code
    )