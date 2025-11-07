# app/api/v1/endpoints/reactions.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.reaction import (
    ReactionCreate,
    ReactionResponse,
    ReactionSummary,
    ReactionDeleteResponse,
    ReactionUpsertResponse
)
from app.services.reaction import reaction_service
from app.api.deps import get_client_ip_from_request

router = APIRouter()


@router.post("/{entity_type}/{entity_id}", response_model=ReactionUpsertResponse, status_code=status.HTTP_200_OK)
async def add_or_update_reaction(
    entity_type: str,
    entity_id: int,
    reaction_data: ReactionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    ip_address = get_client_ip_from_request(request)
    
    entity_exists = await reaction_service.verify_entity_exists(
        db, entity_id, entity_type
    )
    
    if not entity_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.replace('_', ' ').title()} not found"
        )
    
    reaction, action = await reaction_service.upsert_reaction(
        db=db,
        email=reaction_data.email,
        name=reaction_data.name,
        reaction_type=reaction_data.reaction_type,
        entity_id=entity_id,
        entity_type=entity_type,
        ip_address=ip_address
    )
    
    message = f"Your reaction has been {'updated' if action == 'updated' else 'added'} successfully!"
    
    return ReactionUpsertResponse(
        reaction=reaction,
        action=action,
        message=message
    )


@router.get("/{entity_type}/{entity_id}/summary", response_model=ReactionSummary)
async def get_reactions_summary(
    entity_type: str,
    entity_id: int,
    user_email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    entity_exists = await reaction_service.verify_entity_exists(
        db, entity_id, entity_type
    )
    
    if not entity_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.replace('_', ' ').title()} not found"
        )
    
    summary = await reaction_service.get_reaction_summary(
        db=db,
        entity_id=entity_id,
        entity_type=entity_type,
        user_email=user_email
    )
    
    return summary


@router.get("/{entity_type}/{entity_id}", response_model=List[ReactionResponse])
async def get_reactions(
    entity_type: str,
    entity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    entity_exists = await reaction_service.verify_entity_exists(
        db, entity_id, entity_type
    )
    
    if not entity_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.replace('_', ' ').title()} not found"
        )
    
    reactions = await reaction_service.get_all_reactions(
        db=db,
        entity_id=entity_id,
        entity_type=entity_type,
        limit=limit,
        offset=skip
    )
    
    return reactions


@router.delete("/{entity_type}/{entity_id}", response_model=ReactionDeleteResponse)
async def delete_reaction(
    entity_type: str,
    entity_id: int,
    email: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    deleted = await reaction_service.delete_reaction(
        db=db,
        email=email,
        entity_id=entity_id,
        entity_type=entity_type
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found or already deleted"
        )
    
    return ReactionDeleteResponse(
        message="Your reaction has been removed successfully",
        deleted=True
    )