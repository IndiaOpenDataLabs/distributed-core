"""
app/services/storage/minio_storage.py

This module provides a MinIO implementation of the StorageService.
"""

import logging
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from distributed_core.core.config import (
    settings,
)
from distributed_core.plugins import register_plugin
from distributed_core.services.storage.interface import StorageInterface

logger = logging.getLogger(__name__)


@register_plugin(StorageInterface, name="minio")
class MinIOStorageService(StorageInterface):
    """
    A MinIO implementation of the StorageService.
    """

    def __init__(self):
        self._client = Minio(
            endpoint=settings.MINIO_HOST,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,  # Use True for HTTPS
        )

    def upload_file(
        self, bucket_name: str, object_name: str, file_data: BinaryIO, file_size: int
    ):
        """
        Uploads a file to the specified MinIO bucket.
        """
        try:
            found = self._client.bucket_exists(bucket_name)
            if not found:
                self._client.make_bucket(bucket_name)
                logger.info("Bucket '%s' created.", bucket_name)
            self._client.put_object(
                bucket_name,
                object_name,
                file_data,
                file_size,
            )
            logger.info("File '%s' uploaded to bucket '%s'.", object_name, bucket_name)
        except S3Error as e:
            logger.error("Error uploading file to MinIO: %s", e)
            raise

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Downloads a file from the specified MinIO bucket.
        """
        try:
            response = self._client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            logger.error("Error downloading file from MinIO: %s", e)
            raise
        finally:
            if "response" in locals():
                response.close()
                response.release_conn()

    def delete_file(self, bucket_name: str, object_name: str):
        """
        Deletes a file from the specified MinIO bucket.
        """
        try:
            self._client.remove_object(bucket_name, object_name)
            logger.info("File '%s' deleted from bucket '%s'.", object_name, bucket_name)
        except S3Error as e:
            logger.error("Error deleting file from MinIO: %s", e)
            raise
