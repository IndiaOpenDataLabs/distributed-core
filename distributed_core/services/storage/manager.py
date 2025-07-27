"""
app/services/storage/manager.py

This module defines the manager for storage-related services.
"""

from distributed_core.services.storage.base import StorageService
from distributed_core.services.storage.minio_storage import MinIOStorageService
from distributed_core.services.storage.local_file_storage import LocalFileStorageService
from distributed_core.core.config import settings


class StorageManager:
    """
    Manages and provides access to storage-related services.
    """

    _storage_service: StorageService | None = None

    @classmethod
    def get_storage_service(cls) -> StorageService:
        """
        Returns the configured StorageService instance based on settings.
        """
        if cls._storage_service is None:
            if settings.STORAGE_SERVICE_TYPE == "minio":
                cls._storage_service = MinIOStorageService()
            elif settings.STORAGE_SERVICE_TYPE == "local":
                cls._storage_service = LocalFileStorageService()
            else:
                raise ValueError(
                    f"Unknown storage service type: {settings.STORAGE_SERVICE_TYPE}"
                )
        return cls._storage_service
