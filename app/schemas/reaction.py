from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from app.models.reaction import ReactionTypeEnum

class ReactionBase(BaseModel):
    email: EmailStr
    name: str
    reaction_type: ReactionTypeEnum

class ReactionCreate(ReactionBase):
    pass

class ReactionUpdate(BaseModel):
    reaction_type: Optional[ReactionTypeEnum] = None
    name: Optional[str] = None

class ReactionResponse(ReactionBase):
    id: int
    entity_id: int
    entity_type: str
    ip_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ReactionSummary(BaseModel):
    total_reactions: int
    like_count: int
    love_count: int
    congratulations_count: int
    user_reaction: Optional[ReactionTypeEnum] = None

class ReactionDeleteResponse(BaseModel):
    message: str
    deleted: bool

class ReactionUpsertResponse(BaseModel):
    reaction: ReactionResponse
    action: Literal["created", "updated"]
    message: str