# app/api/v1/endpoints/blog.py (VERSIÓN MEJORADA)

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.db.repositories.blog import blog_repository
from app.models.user import User
from app.schemas.blog import (
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostWithDetails
)
from app.schemas.project import CommentCreate, CommentResponse
from app.schemas.media import ImageResponse, ImageUploadResponse, ImageUpdate, VideoCreate, VideoResponse
from app.services.media import media_service
from app.services.email import email_service
from app.services.notification import notification_service  # NUEVO
from app.api.deps import get_current_admin
from app.models.project import Comment

router = APIRouter()


@router.get("/", response_model=List[BlogPostResponse])
async def get_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    published: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
):
    posts = await blog_repository.get_all_ordered(
        db, skip=skip, limit=limit, published=published
    )
    
    if posts:
        post_ids = [p.id for p in posts]
        images_dict = await media_service.load_images_for_entities(
            db, post_ids, 'blog_post'
        )
        
        for post in posts:
            post.images = images_dict.get(post.id, [])
    
    return posts


@router.get("/{slug}", response_model=BlogPostWithDetails)
async def get_blog_post(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    post_db = await blog_repository.get_by_slug_with_details(db, slug)
    
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    approved_comments = [c for c in post_db.comments if c.approved]
    images = await media_service.get_images(db, post_db.id, 'blog_post')

    response_data = BlogPostWithDetails.model_validate(post_db)
    
    response_data.comments = approved_comments
    response_data.images = images
    
    await blog_repository.increment_views(db, post_db.id)
    
    return response_data


@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    background_tasks: BackgroundTasks,  # NUEVO
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Crear nuevo blog post.
    Si está publicado, notifica automáticamente a los suscriptores.
    """
    existing_post = await blog_repository.get_by_slug(db, post_data.slug)
    
    if existing_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post with this slug already exists"
        )
    
    post = await blog_repository.create(db, obj_in=post_data)
    post.images = []
    
    # NUEVO: Notificar a suscriptores si el post está publicado
    if post.published:
        background_tasks.add_task(
            notification_service.notify_new_blog_post,
            db,
            post.title,
            post.slug,
            post.excerpt or "Check out my latest blog post!"
        )
    
    return post


@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Actualizar blog post existente.
    NO envía notificaciones en actualizaciones.
    """
    post = await blog_repository.get(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    if post_data.slug and post_data.slug != post.slug:
        existing_post = await blog_repository.get_by_slug(db, post_data.slug)
        
        if existing_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A post with this slug already exists"
            )
    
    post = await blog_repository.update(db, db_obj=post, obj_in=post_data)
    post.images = await media_service.get_images(db, post_id, 'blog_post')
    
    # NO notificamos en actualizaciones, solo en creación
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = await blog_repository.delete(db, id=post_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )


# ==================== IMÁGENES ====================

@router.post("/{post_id}/images/upload", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_blog_image(
    post_id: int,
    file: UploadFile = File(...),
    image_order: int = Form(1, ge=1),
    alt_text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    post = await blog_repository.get(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    image = await media_service.upload_and_create_image(
        db=db,
        file=file,
        entity_id=post_id,
        entity_type='blog_post',
        image_order=image_order,
        alt_text=alt_text
    )
    
    return ImageUploadResponse(
        message="Image uploaded successfully",
        image=image
    )


@router.put("/{post_id}/images/{image_id}", response_model=ImageResponse)
async def update_blog_image_metadata(
    post_id: int,
    image_id: int,
    image_data: ImageUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    image = await media_service.update_image(
        db=db,
        image_id=image_id,
        entity_id=post_id,
        entity_type='blog_post',
        image_order=image_data.image_order,
        alt_text=image_data.alt_text
    )
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return image


@router.put("/{post_id}/images/{image_id}/replace", response_model=ImageUploadResponse)
async def replace_blog_image(
    post_id: int,
    image_id: int,
    file: UploadFile = File(...),
    image_order: Optional[int] = Form(None, ge=1),
    alt_text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    image = await media_service.replace_image(
        db=db,
        image_id=image_id,
        entity_id=post_id,
        entity_type='blog_post',
        new_file=file,
        image_order=image_order,
        alt_text=alt_text
    )
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return ImageUploadResponse(
        message="Image replaced successfully",
        image=image
    )


@router.delete("/{post_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_image(
    post_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = await media_service.delete_image(
        db=db,
        image_id=image_id,
        entity_id=post_id,
        entity_type='blog_post'
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )


# ==================== COMENTARIOS ====================

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_blog_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db)
):
    post = await blog_repository.get(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    comment = Comment(
        name=comment_data.name,
        email=comment_data.email,
        content=comment_data.content,
        blog_post_id=post_id,
        approved=False
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    try:
        await email_service.send_comment_notification(
            commenter_name=comment_data.name,
            commenter_email=comment_data.email,
            comment_content=comment_data.content,
            item_type="blog_post",
            item_title=post.title
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")
    
    return comment


# ==================== VIDEOS ====================

@router.post("/{post_id}/videos", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def add_blog_video(
    post_id: int,
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    post = await blog_repository.get(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    video = await media_service.add_video(
        db,
        post_id,
        'blog_post',
        video_data.title,
        video_data.url,
        video_data.source,
        video_data.thumbnail_url
    )
    
    return video