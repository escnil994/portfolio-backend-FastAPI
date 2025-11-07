from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError, AzureError
from fastapi import UploadFile, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid
import os
from pathlib import Path

from app.config import settings


class AzureStorageService:
    """Service for managing Azure Blob Storage operations"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize Azure Blob Service Client"""
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
            self._ensure_container_exists()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure Storage: {str(e)}")
    
    def _ensure_container_exists(self):
        """Ensure the storage container exists, create if not"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container(public_access='blob')
        except Exception as e:
            print(f"Warning: Could not verify/create container: {e}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size"""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (read first chunk to verify it's not empty)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
    
    def _generate_blob_name(self, original_filename: str, entity_type: str, entity_id: int) -> str:
        """Generate unique blob name with structure: entity_type/entity_id/uuid_filename"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex[:12]
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        
        # Clean original filename
        clean_name = Path(original_filename).stem
        clean_name = "".join(c for c in clean_name if c.isalnum() or c in ('-', '_'))[:50]
        
        return f"{entity_type}/{entity_id}/{timestamp}_{unique_id}_{clean_name}{file_ext}"
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext_to_content_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        file_ext = Path(filename).suffix.lower()
        return ext_to_content_type.get(file_ext, 'application/octet-stream')
    
    async def upload_image(
        self,
        file: UploadFile,
        entity_type: str,
        entity_id: int
    ) -> Tuple[str, str]:
        """
        Upload image to Azure Blob Storage
        
        Args:
            file: The uploaded file
            entity_type: Type of entity (project, blog_post, profile)
            entity_id: ID of the entity
            
        Returns:
            Tuple of (blob_url, blob_name)
        """
        try:
            # Validate file
            self._validate_file(file)
            
            # Generate blob name
            blob_name = self._generate_blob_name(file.filename, entity_type, entity_id)
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Set content settings
            content_settings = ContentSettings(
                content_type=self._get_content_type(file.filename),
                cache_control='public, max-age=31536000'  # Cache for 1 year
            )
            
            # Read and upload file
            file_content = await file.read()
            
            blob_client.upload_blob(
                file_content,
                content_settings=content_settings,
                overwrite=False  # Prevent accidental overwrites
            )
            
            # Get the public URL
            blob_url = blob_client.url
            
            return blob_url, blob_name
            
        except HTTPException:
            raise
        except AzureError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Azure Storage error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    async def delete_image(self, blob_name: str) -> bool:
        """
        Delete image from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
            
        except ResourceNotFoundError:
            return False
        except AzureError as e:
            print(f"Azure error deleting blob {blob_name}: {e}")
            return False
        except Exception as e:
            print(f"Error deleting blob {blob_name}: {e}")
            return False
    
    async def delete_images_batch(self, blob_names: list[str]) -> dict[str, bool]:
        """
        Delete multiple images from Azure Blob Storage
        
        Args:
            blob_names: List of blob names to delete
            
        Returns:
            Dictionary mapping blob_name to deletion success status
        """
        results = {}
        for blob_name in blob_names:
            results[blob_name] = await self.delete_image(blob_name)
        return results
    
    def extract_blob_name_from_url(self, url: str) -> Optional[str]:
        """
        Extract blob name from Azure blob URL
        
        Args:
            url: Full blob URL
            
        Returns:
            Blob name or None if not a valid Azure URL
        """
        try:
            # Azure blob URLs format: https://{account}.blob.core.windows.net/{container}/{blob_name}
            if 'blob.core.windows.net' not in url:
                return None
            
            parts = url.split(f'/{self.container_name}/')
            if len(parts) == 2:
                # Remove query parameters if present
                blob_name = parts[1].split('?')[0]
                return blob_name
            
            return None
        except Exception:
            return None
    
    def generate_sas_url(self, blob_name: str, expiry_hours: int = 1) -> str:
        """
        Generate a SAS URL for temporary access (useful for private containers)
        
        Args:
            blob_name: Name of the blob
            expiry_hours: Hours until the SAS token expires
            
        Returns:
            URL with SAS token
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            return f"{blob_client.url}?{sas_token}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate SAS URL: {str(e)}"
            )


# Singleton instance
azure_storage_service = AzureStorageService()