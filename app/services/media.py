from typing import List, Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from fastapi import HTTPException, status, UploadFile

from app.models.media import Image, Video
from app.core.azure_storage import azure_storage_service


EntityType = Literal["project", "blog_post", "profile"]


class MediaService:
    """Service for managing media (images and videos) with Azure Blob Storage integration"""
    
    
    async def get_images(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: EntityType
    ) -> List[Image]:
        """Get all images for a specific entity, ordered by image_order"""
        query = select(Image).where(
            and_(
                Image.entity_id == entity_id,
                Image.entity_type == entity_type
            )
        ).order_by(Image.image_order)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_image(
        self,
        db: AsyncSession,
        image_id: int,
        entity_id: int,
        entity_type: EntityType
    ) -> Optional[Image]:
        """Get a specific image by ID, entity_id and entity_type"""
        query = select(Image).where(
            and_(
                Image.id == image_id,
                Image.entity_id == entity_id,
                Image.entity_type == entity_type
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def upload_and_create_image(
        self,
        db: AsyncSession,
        file: UploadFile,
        entity_id: int,
        entity_type: EntityType,
        image_order: int = 1,
        alt_text: Optional[str] = None,
        *,
        commit: bool = True
    ) -> Image:
        """
        Upload image to Azure Blob Storage and create database record
        
        Args:
            db: Database session
            file: Uploaded file
            entity_id: ID of the entity (project, blog_post, profile)
            entity_type: Type of entity
            image_order: Order for displaying images
            alt_text: Alternative text for accessibility
            commit: Whether to commit the transaction
            
        Returns:
            Created Image object with Azure blob URL
        """
        try:
            blob_url, blob_name = await azure_storage_service.upload_image(
                file=file,
                entity_type=entity_type,
                entity_id=entity_id
            )
            
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            image = Image(
                entity_id=entity_id,
                entity_type=entity_type,
                image_url=blob_url,
                blob_name=blob_name,
                image_order=image_order,
                alt_text=alt_text,
                file_size=file_size,
                content_type=file.content_type
            )
            
            db.add(image)
            
            if commit:
                await db.commit()
                await db.refresh(image)
            
            return image
            
        except HTTPException:
            raise
        except Exception as e:
            if 'blob_name' in locals():
                await azure_storage_service.delete_image(blob_name)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create image record: {str(e)}"
            )
    
    async def add_image(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: EntityType,
        image_url: str,
        image_order: int = 1,
        alt_text: Optional[str] = None,
        *,
        commit: bool = True
    ) -> Image:
        """
        Add image with external URL (legacy method for compatibility)
        Use upload_and_create_image for new implementations
        """
        if not image_url or len(image_url) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image URL"
            )
        
        image = Image(
            entity_id=entity_id,
            entity_type=entity_type,
            image_url=image_url,
            image_order=image_order,
            alt_text=alt_text
        )
        
        db.add(image)
        
        if commit:
            await db.commit()
            await db.refresh(image)
        
        return image
    
    async def update_image(
        self,
        db: AsyncSession,
        image_id: int,
        entity_id: int,
        entity_type: EntityType,
        *,
        image_order: Optional[int] = None,
        alt_text: Optional[str] = None,
        commit: bool = True
    ) -> Optional[Image]:
        """
        Update image metadata (order, alt_text)
        Note: Does not support replacing the image file itself
        """
        image = await self.get_image(db, image_id, entity_id, entity_type)
        
        if not image:
            return None
        
        if image_order is not None:
            image.image_order = image_order
        
        if alt_text is not None:
            image.alt_text = alt_text
        
        if commit:
            await db.commit()
            await db.refresh(image)
        
        return image
    
    async def replace_image(
        self,
        db: AsyncSession,
        image_id: int,
        entity_id: int,
        entity_type: EntityType,
        new_file: UploadFile,
        *,
        image_order: Optional[int] = None,
        alt_text: Optional[str] = None,
        commit: bool = True
    ) -> Optional[Image]:
        """
        Replace an existing image with a new file
        Deletes old blob and uploads new one
        """
        # Get existing image
        image = await self.get_image(db, image_id, entity_id, entity_type)
        
        if not image:
            return None
        
        old_blob_name = image.blob_name
        
        try:
            # Upload new image to Azure
            blob_url, blob_name = await azure_storage_service.upload_image(
                file=new_file,
                entity_type=entity_type,
                entity_id=entity_id
            )
            
            # Get file size
            new_file.file.seek(0, 2)
            file_size = new_file.file.tell()
            new_file.file.seek(0)
            
            # Update image record
            image.image_url = blob_url
            image.blob_name = blob_name
            image.file_size = file_size
            image.content_type = new_file.content_type
            
            if image_order is not None:
                image.image_order = image_order
            
            if alt_text is not None:
                image.alt_text = alt_text
            
            if commit:
                await db.commit()
                await db.refresh(image)
            
            # Delete old blob from Azure (fire and forget)
            if old_blob_name:
                await azure_storage_service.delete_image(old_blob_name)
            
            return image
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up new blob if database update fails
            if 'blob_name' in locals():
                await azure_storage_service.delete_image(blob_name)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to replace image: {str(e)}"
            )
    
    async def delete_image(
        self,
        db: AsyncSession,
        image_id: int,
        entity_id: int,
        entity_type: EntityType,
        *,
        commit: bool = True
    ) -> bool:
        """
        Delete image from database and Azure Blob Storage
        """
        image = await self.get_image(db, image_id, entity_id, entity_type)
        
        if not image:
            return False
        
        blob_name = image.blob_name
        
        await db.delete(image)
        
        if commit:
            await db.commit()
        
        if blob_name:
            await azure_storage_service.delete_image(blob_name)
        
        return True
    
    async def delete_all_images(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: EntityType,
        *,
        commit: bool = True
    ) -> int:
        """
        Delete all images for an entity from database and Azure Blob Storage
        """
        images = await self.get_images(db, entity_id, entity_type)
        blob_names = [img.blob_name for img in images if img.blob_name]
        
        query = delete(Image).where(
            and_(
                Image.entity_id == entity_id,
                Image.entity_type == entity_type
            )
        )
        
        result = await db.execute(query)
        
        if commit:
            await db.commit()
        
        if blob_names:
            await azure_storage_service.delete_images_batch(blob_names)
        
        return result.rowcount
    
    async def load_images_for_entities(
        self,
        db: AsyncSession,
        entity_ids: List[int],
        entity_type: EntityType
    ) -> dict[int, List[Image]]:
        """
        Load images for multiple entities efficiently (prevents N+1 queries)
        """
        if not entity_ids:
            return {}
        
        query = select(Image).where(
            and_(
                Image.entity_id.in_(entity_ids),
                Image.entity_type == entity_type
            )
        ).order_by(Image.entity_id, Image.image_order)
        
        result = await db.execute(query)
        all_images = result.scalars().all()
        
        images_by_entity = {}
        for img in all_images:
            if img.entity_id not in images_by_entity:
                images_by_entity[img.entity_id] = []
            images_by_entity[img.entity_id].append(img)
        
        return images_by_entity
    
    # ==================== VIDEO OPERATIONS ====================
    
    async def get_videos(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: Literal["project", "blog_post"]
    ) -> List[Video]:
        """Get all videos for a specific entity"""
        if entity_type == "project":
            filter_condition = Video.project_id == entity_id
        elif entity_type == "blog_post":
            filter_condition = Video.blog_post_id == entity_id
        else:
            raise ValueError(f"Invalid entity_type for videos: {entity_type}")
        
        query = select(Video).where(filter_condition).order_by(Video.created_at)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_video(
        self,
        db: AsyncSession,
        video_id: int,
        entity_id: int,
        entity_type: Literal["project", "blog_post"]
    ) -> Optional[Video]:
        """Get a specific video by ID"""
        if entity_type == "project":
            filter_condition = and_(Video.id == video_id, Video.project_id == entity_id)
        elif entity_type == "blog_post":
            filter_condition = and_(Video.id == video_id, Video.blog_post_id == entity_id)
        else:
            raise ValueError(f"Invalid entity_type for videos: {entity_type}")
        
        query = select(Video).where(filter_condition)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def add_video(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: Literal["project", "blog_post"],
        title: str,
        url: str,
        source: str,
        thumbnail_url: Optional[str] = None,
        *,
        commit: bool = True
    ) -> Video:
        """Add a video to an entity"""
        video_dict = {
            "title": title,
            "url": url,
            "source": source,
            "thumbnail_url": thumbnail_url
        }
        
        if entity_type == "project":
            video_dict["project_id"] = entity_id
        elif entity_type == "blog_post":
            video_dict["blog_post_id"] = entity_id
        else:
            raise ValueError(f"Invalid entity_type for videos: {entity_type}")
        
        video = Video(**video_dict)
        db.add(video)
        
        if commit:
            await db.commit()
            await db.refresh(video)
        
        return video
    
    async def delete_video(
        self,
        db: AsyncSession,
        video_id: int,
        entity_id: int,
        entity_type: Literal["project", "blog_post"],
        *,
        commit: bool = True
    ) -> bool:
        """Delete a video"""
        video = await self.get_video(db, video_id, entity_id, entity_type)
        
        if not video:
            return False
        
        await db.delete(video)
        
        if commit:
            await db.commit()
        
        return True


media_service = MediaService()