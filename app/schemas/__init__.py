# app/schemas/__init__.py

from app.schemas.auth import (
    Token,
    LoginRequest,
    Verify2FARequest,
    EnableTOTPRequest,
    EnableTOTPResponse,
    VerifyTOTPRequest,
    PasswordChangeRequest
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.schemas.profile import (
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithDetails,
    CommentBase,
    CommentCreate,
    CommentResponse
)
from app.schemas.blog import (
    BlogPostBase,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostWithDetails
)
from app.schemas.media import (
    ImageBase,
    ImageCreate,
    ImageUpdate,
    ImageResponse,
    VideoBase,
    VideoCreate,
    VideoResponse
)
from app.schemas.reaction import (
    ReactionCreate,
    ReactionUpdate,
    ReactionResponse,
    ReactionSummary,
    ReactionDeleteResponse,
    ReactionUpsertResponse
)
from app.schemas.contact import (
    ContactMessageBase,
    ContactMessageCreate,
    ContactMessageResponse,
    MessageResponse
)

__all__ = [
    "Token",
    "LoginRequest",
    "Verify2FARequest",
    "EnableTOTPRequest",
    "EnableTOTPResponse",
    "VerifyTOTPRequest",
    "PasswordChangeRequest",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectWithDetails",
    "CommentBase",
    "CommentCreate",
    "CommentResponse",
    "BlogPostBase",
    "BlogPostCreate",
    "BlogPostUpdate",
    "BlogPostResponse",
    "BlogPostWithDetails",
    "ImageBase",
    "ImageCreate",
    "ImageUpdate",
    "ImageResponse",
    "VideoBase",
    "VideoCreate",
    "VideoResponse",
    "ReactionCreate",
    "ReactionUpdate",
    "ReactionResponse",
    "ReactionSummary",
    "ReactionDeleteResponse",
    "ReactionUpsertResponse",
    "ContactMessageBase",
    "ContactMessageCreate",
    "ContactMessageResponse",
    "MessageResponse"
]