from typing import List, Optional, Literal, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from fastapi import HTTPException, status, UploadFile

from app.models.media import Image, Video
from app.core.azure_storage import azure_storage_service

EntityType = Literal["project", "blog_post", "profile"]

class MediaService:
    
    async def get_images(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: EntityType
    ) -> List[Image]:
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
        try:
            # CORRECCIÓN: Usar file.size directamente
            file_size = file.size
            
            blob_url, blob_name = await azure_storage_service.upload_image(
                file=file,
                entity_type=entity_type,
                entity_id=entity_id
            )
            
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
            if 'blob_name' in locals() and blob_name:
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
        image = await self.get_image(db, image_id, entity_id, entity_type)
        
        if not image:
            return None
        
        old_blob_name = image.blob_name
        
        try:
            # CORRECCIÓN: Usar new_file.size directamente
            file_size = new_file.size

            blob_url, blob_name = await azure_storage_service.upload_image(
                file=new_file,
                entity_type=entity_type,
                entity_id=entity_id
            )
            
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
            
            if old_blob_name:
                await azure_storage_service.delete_image(old_blob_name)
            
            return image
            
        except HTTPException:
            raise
        except Exception as e:
            if 'blob_name' in locals() and blob_name:
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
    ) -> Dict[int, List[Image]]:
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
        video = await self.get_video(db, video_id, entity_id, entity_type)
        
        if not video:
            return False
        
        await db.delete(video)
        
        if commit:
            await db.commit()
        
        return True

media_service = MediaService()