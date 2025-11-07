# scripts/seed_data.py

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import AsyncSessionLocal
from app.models.profile import Profile
from app.models.project import Project
from app.models.blog import BlogPost
from app.models.media import Image


async def seed_profile(db):
    print("Seeding profile...")
    
    profile = Profile(
        username="johndoe",
        name="John",
        last_name="Doe",
        display_name="John Doe",
        title="Full Stack Developer & DevOps Specialist",
        bio="Passionate developer with 5+ years of experience in building scalable web applications.",
        email="john.doe@example.com",
        github_url="https://github.com/johndoe",
        linkedin_url="https://linkedin.com/in/johndoe",
        twitter_url="https://twitter.com/johndoe",
        skills="Python, JavaScript, React, FastAPI, Docker, Kubernetes, AWS",
        resume_url="https://example.com/resume.pdf"
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    print(f"✅ Profile created: {profile.display_name}")
    return profile


async def seed_projects(db):
    print("Seeding projects...")
    
    projects_data = [
        {
            "title": "E-Commerce Platform",
            "description": "A full-featured e-commerce platform with payment integration",
            "content": "Built with React, Node.js, and MongoDB. Features include user authentication, product catalog, shopping cart, and Stripe payment integration.",
            "technologies": "React, Node.js, MongoDB, Stripe, Docker",
            "github_url": "https://github.com/johndoe/ecommerce-platform",
            "demo_url": "https://ecommerce-demo.example.com",
            "featured": True
        },
        {
            "title": "Task Management API",
            "description": "RESTful API for task and project management",
            "content": "FastAPI-based REST API with JWT authentication, PostgreSQL database, and comprehensive documentation.",
            "technologies": "Python, FastAPI, PostgreSQL, Docker, Redis",
            "github_url": "https://github.com/johndoe/task-api",
            "demo_url": "https://task-api-demo.example.com",
            "featured": True
        },
        {
            "title": "Real-time Chat Application",
            "description": "WebSocket-based chat application with rooms and private messaging",
            "content": "Real-time communication app built with Socket.io, Express, and React. Features include public rooms, private messages, and online presence indicators.",
            "technologies": "React, Express, Socket.io, MongoDB",
            "github_url": "https://github.com/johndoe/chat-app",
            "demo_url": "https://chat-demo.example.com",
            "featured": False
        }
    ]
    
    projects = []
    for data in projects_data:
        project = Project(**data)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        projects.append(project)
        print(f"✅ Project created: {project.title}")
    
    return projects


async def seed_blog_posts(db):
    print("Seeding blog posts...")
    
    posts_data = [
        {
            "title": "Getting Started with FastAPI",
            "slug": "getting-started-with-fastapi",
            "excerpt": "Learn how to build modern APIs with FastAPI",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints...",
            "author": "John Doe",
            "tags": "python, fastapi, tutorial, api",
            "published": True
        },
        {
            "title": "Docker Best Practices",
            "slug": "docker-best-practices",
            "excerpt": "Essential tips for working with Docker in production",
            "content": "Docker has become an essential tool for modern development. Here are some best practices...",
            "author": "John Doe",
            "tags": "docker, devops, containers, best-practices",
            "published": True
        },
        {
            "title": "Building Scalable Microservices",
            "slug": "building-scalable-microservices",
            "excerpt": "Architecture patterns for microservices",
            "content": "Microservices architecture has gained popularity for building scalable applications...",
            "author": "John Doe",
            "tags": "microservices, architecture, scalability, patterns",
            "published": True
        }
    ]
    
    posts = []
    for data in posts_data:
        post = BlogPost(**data)
        db.add(post)
        await db.commit()
        await db.refresh(post)
        posts.append(post)
        print(f"✅ Blog post created: {post.title}")
    
    return posts


async def seed_database():
    print("=" * 60)
    print("Database Seeding")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            profile = await seed_profile(db)
            print()
            
            projects = await seed_projects(db)
            print()
            
            posts = await seed_blog_posts(db)
            print()
            
            print("=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)
            print()
            print(f"Created:")
            print(f"  - 1 Profile")
            print(f"  - {len(projects)} Projects")
            print(f"  - {len(posts)} Blog Posts")
            print()
            
        except Exception as e:
            print(f"\n❌ Error seeding database: {e}")
            await db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_database())