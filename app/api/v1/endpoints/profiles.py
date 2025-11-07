# app/api/v1/endpoints/profiles.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.db.repositories.base import BaseRepository
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.schemas.media import ImageResponse
from app.services.media import media_service
from app.api.deps import get_current_admin

router = APIRouter()

profile_repo = BaseRepository[Profile, ProfileCreate, ProfileUpdate](Profile)


@router.get("/", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    profiles = await profile_repo.get_multi(db, limit=1)
    
    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile = profiles[0]
    profile.images = await media_service.get_images(db, profile.id, 'profile')
    
    return profile


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing_profiles = await profile_repo.get_multi(db, limit=1)
    
    if existing_profiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )
    
    profile = await profile_repo.create(db, obj_in=profile_data)
    profile.images = []
    
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    profile = await profile_repo.get(db, profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile = await profile_repo.update(db, db_obj=profile, obj_in=profile_data)
    profile.images = await media_service.get_images(db, profile_id, 'profile')
    
    return profile


@router.post("/{profile_id}/images", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def add_profile_image(
    profile_id: int,
    image_url: str,
    image_order: int = Query(1, ge=1),
    alt_text: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    profile = await profile_repo.get(db, profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    image = await media_service.add_image(
        db, profile_id, 'profile', image_url, image_order, alt_text
    )
    
    return image


@router.delete("/{profile_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_image(
    profile_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = await media_service.delete_image(db, image_id, profile_id, 'profile')
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )