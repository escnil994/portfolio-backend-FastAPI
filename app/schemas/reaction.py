# app/schemas/reaction.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.reaction import ReactionTypeEnum


class ReactionCreate(BaseModel):
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., min_length=1, max_length=255, description="User name")
    reaction_type: ReactionTypeEnum = Field(..., description="Reaction type: like, love, congratulations")


class ReactionUpdate(BaseModel):
    reaction_type: ReactionTypeEnum = Field(..., description="New reaction type")


class ReactionResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    reaction_type: ReactionTypeEnum
    entity_id: int
    entity_type: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReactionSummary(BaseModel):
    total_reactions: int = Field(0, description="Total reactions")
    like_count: int = Field(0, description="Number of likes")
    love_count: int = Field(0, description="Number of loves")
    congratulations_count: int = Field(0, description="Number of congratulations")
    user_reaction: Optional[ReactionTypeEnum] = Field(None, description="Current user reaction")


class ReactionDeleteResponse(BaseModel):
    message: str
    deleted: bool


class ReactionUpsertResponse(BaseModel):
    reaction: ReactionResponse
    action: str = Field(..., description="'created' or 'updated'")
    message: str