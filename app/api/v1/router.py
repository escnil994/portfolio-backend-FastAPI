# app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import auth, profiles, projects, blog, contact, reactions, subscribers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(reactions.router, prefix="/reactions", tags=["Reactions"])
api_router.include_router(subscribers.router, prefix="/subscribes", tags=["Subscribes"])