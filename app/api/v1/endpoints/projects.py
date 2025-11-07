from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.db.repositories.project import project_repository
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithDetails,
    CommentCreate,
    CommentResponse
)
from app.schemas.media import ImageResponse, ImageUploadResponse, ImageUpdate, VideoCreate, VideoResponse
from app.services.media import media_service
from app.services.email import email_service
from app.services.notification import notification_service
from app.api.deps import get_current_admin
from app.models.project import Comment

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    projects = await project_repository.get_all_ordered(
        db, skip=skip, limit=limit, featured=featured
    )
    
    if projects:
        project_ids = [p.id for p in projects]
        images_dict = await media_service.load_images_for_entities(
            db, project_ids, 'project'
        )
        
        for project in projects:
            project.images = images_dict.get(project.id, [])
    
    return projects


@router.get("/{project_id}", response_model=ProjectWithDetails)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    project = await project_repository.get_with_details(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.images = await media_service.get_images(db, project_id, 'project')
    project.comments = [c for c in project.comments if c.approved]
    
    return project


@router.post("/admin/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,  # NUEVO
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Crear nuevo proyecto.
    Notifica automáticamente a los suscriptores.
    """
    project = await project_repository.create(db, obj_in=project_data)
    project.images = []
    
    # NUEVO: Notificar a suscriptores sobre el nuevo proyecto
    background_tasks.add_task(
        notification_service.notify_new_project,
        db,
        project.title,
        project.id,
        project.description
    )
    
    return project


@router.put("/admin/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Actualizar proyecto existente.
    NO envía notificaciones en actualizaciones.
    """
    project = await project_repository.get(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = await project_repository.update(db, db_obj=project, obj_in=project_data)
    project.images = await media_service.get_images(db, project_id, 'project')
    
    # NO notificamos en actualizaciones, solo en creación
    
    return project


@router.delete("/admin/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = await project_repository.delete(db, id=project_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


# ==================== IMÁGENES ====================

@router.post("/admin/{project_id}/images/upload", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    image_order: int = Form(1, ge=1),
    alt_text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    project = await project_repository.get(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    image = await media_service.upload_and_create_image(
        db=db,
        file=file,
        entity_id=project_id,
        entity_type='project',
        image_order=image_order,
        alt_text=alt_text
    )
    
    return ImageUploadResponse(
        message="Image uploaded successfully",
        image=image
    )


@router.put("/admin/{project_id}/images/{image_id}", response_model=ImageResponse)
async def update_project_image_metadata(
    project_id: int,
    image_id: int,
    image_data: ImageUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    image = await media_service.update_image(
        db=db,
        image_id=image_id,
        entity_id=project_id,
        entity_type='project',
        image_order=image_data.image_order,
        alt_text=image_data.alt_text
    )
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return image


@router.put("/admin/{project_id}/images/{image_id}/replace", response_model=ImageUploadResponse)
async def replace_project_image(
    project_id: int,
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
        entity_id=project_id,
        entity_type='project',
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


@router.delete("/admin/{project_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_image(
    project_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = await media_service.delete_image(
        db=db,
        image_id=image_id,
        entity_id=project_id,
        entity_type='project'
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )


# ==================== COMENTARIOS ====================

@router.post("/{project_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_project_comment(
    project_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db)
):
    project = await project_repository.get(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    comment = Comment(
        name=comment_data.name,
        email=comment_data.email,
        content=comment_data.content,
        project_id=project_id,
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
            item_type="project",
            item_title=project.title
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")
    
    return comment


# ==================== VIDEOS ====================

@router.post("/admin/{project_id}/videos", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def add_project_video(
    project_id: int,
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    project = await project_repository.get(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    video = await media_service.add_video(
        db,
        project_id,
        'project',
        video_data.title,
        video_data.url,
        video_data.source,
        video_data.thumbnail_url
    )
    
    return video