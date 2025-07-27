"""
app/services/storage/local_file_storage.py

This module provides a local file system implementation of the StorageService.
"""

import logging
import os
from typing import BinaryIO

from distributed_core.core.config import settings
from distributed_core.services.storage.base import StorageService

logger = logging.getLogger(__name__)


class LocalFileStorageService(StorageService):
    """
    A local file system implementation of the StorageService.
    """

    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def _get_full_path(self, bucket_name: str, object_name: str) -> str:
        bucket_path = os.path.join(self.base_path, bucket_name)
        os.makedirs(bucket_path, exist_ok=True)
        return os.path.join(bucket_path, object_name)

    def upload_file(
        self, bucket_name: str, object_name: str, file_data: BinaryIO, file_size: int
    ):
        full_path = self._get_full_path(bucket_name, object_name)
        try:
            with open(full_path, "wb") as f:
                f.write(file_data.read())
            logger.info(
                "File '%s' uploaded to local storage in bucket '%s'.",
                object_name,
                bucket_name,
            )
        except Exception as e:
            logger.error("Error uploading file to local storage: %s", e)
            raise

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        full_path = self._get_full_path(bucket_name, object_name)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File '{object_name}' not found in local storage.")
        try:
            with open(full_path, "rb") as f:
                content = f.read()
            logger.info(
                "File '%s' downloaded from local storage in bucket '%s'.",
                object_name,
                bucket_name,
            )
            return content
        except Exception as e:
            logger.error("Error downloading file from local storage: %s", e)
            raise

    def delete_file(self, bucket_name: str, object_name: str):
        full_path = self._get_full_path(bucket_name, object_name)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                logger.info(
                    "File '%s' deleted from local storage in bucket '%s'.",
                    object_name,
                    bucket_name,
                )
            except Exception as e:
                logger.error("Error deleting file from local storage: %s", e)
                raise
        else:
            logger.warning(
                "Attempted to delete non-existent file '%s' from local storage.",
                object_name,
            )
