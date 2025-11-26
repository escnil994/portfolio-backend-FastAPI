from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceNotFoundError
from fastapi import UploadFile, HTTPException, status
from datetime import datetime, timezone
from typing import Tuple, Literal
import uuid
from pathlib import Path

from app.config import settings

class AzureStorageService:
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm', '.avi', '.mkv'}
    
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
    
    async def _get_client(self) -> BlobServiceClient:
        return BlobServiceClient.from_connection_string(self.connection_string)
    
    async def _validate_file(self, file: UploadFile, file_type: Literal['image', 'video']) -> None:
        file_ext = Path(file.filename).suffix.lower()
        
        if file_type == 'image':
            allowed = self.ALLOWED_IMAGE_EXTENSIONS
            max_size = self.MAX_IMAGE_SIZE
        else:
            allowed = self.ALLOWED_VIDEO_EXTENSIONS
            max_size = self.MAX_VIDEO_SIZE
            
        if file_ext not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {file_type} type. Allowed: {', '.join(allowed)}"
            )
        
        # CORRECCIÓN: Usar file.size directamente en lugar de seek(0, 2)
        # FastAPI ya calcula esto al recibir el archivo
        file_size = file.size
        
        if not file_size or file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        if file_size > max_size:
            limit_mb = max_size / 1024 / 1024
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size for {file_type}s: {limit_mb}MB"
            )
        
        # Asegurarnos que el puntero esté al inicio antes de subir
        await file.seek(0)
    
    def _generate_blob_name(self, original_filename: str, entity_type: str, entity_id: int) -> str:
        file_ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        
        clean_name = Path(original_filename).stem
        clean_name = "".join(c for c in clean_name if c.isalnum() or c in ('-', '_'))[:50]
        
        return f"{entity_type}/{entity_id}/{timestamp}_{unique_id}_{clean_name}{file_ext}"
    
    def _get_content_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        types = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif',
            '.webp': 'image/webp', '.svg': 'image/svg+xml',
            '.mp4': 'video/mp4', '.mov': 'video/quicktime',
            '.webm': 'video/webm', '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska'
        }
        return types.get(ext, 'application/octet-stream')
    
    async def _upload_file(
        self,
        file: UploadFile,
        entity_type: str,
        entity_id: int,
        file_type: Literal['image', 'video']
    ) -> Tuple[str, str]:
        try:
            await self._validate_file(file, file_type)
            blob_name = self._generate_blob_name(file.filename, entity_type, entity_id)
            content_type = self._get_content_type(file.filename)
            
            async with await self._get_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(self.container_name)
                
                if not await container_client.exists():
                    await container_client.create_container(public_access='blob')
                
                blob_client = container_client.get_blob_client(blob_name)
                
                # Leer contenido
                file_content = await file.read()
                
                await blob_client.upload_blob(
                    file_content,
                    content_settings=ContentSettings(
                        content_type=content_type,
                        cache_control='public, max-age=31536000'
                    ),
                    overwrite=False
                )
                
                return blob_client.url, blob_name
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file_type}: {str(e)}"
            )
        finally:
            await file.seek(0)

    async def upload_image(self, file: UploadFile, entity_type: str, entity_id: int) -> Tuple[str, str]:
        return await self._upload_file(file, entity_type, entity_id, 'image')

    async def upload_video(self, file: UploadFile, entity_type: str, entity_id: int) -> Tuple[str, str]:
        return await self._upload_file(file, entity_type, entity_id, 'video')
    
    async def delete_image(self, blob_name: str) -> bool:
        if not blob_name:
            return False
        try:
            async with await self._get_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(self.container_name)
                blob_client = container_client.get_blob_client(blob_name)
                await blob_client.delete_blob()
                return True
        except ResourceNotFoundError:
            return False
        except Exception:
            return False
    
    async def delete_images_batch(self, blob_names: list[str]) -> dict[str, bool]:
        results = {}
        for blob_name in blob_names:
            results[blob_name] = await self.delete_image(blob_name)
        return results

azure_storage_service = AzureStorageService()