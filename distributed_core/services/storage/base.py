"""
app/services/storage/base.py

This module defines the base classes for storage services.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    """
    Base class for storage services.
    """

    @abstractmethod
    def upload_file(
        self, bucket_name: str, object_name: str, file_data: BinaryIO, file_size: int
    ):
        """
        Uploads a file to the specified bucket.
        """

    @abstractmethod
    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Downloads a file from the specified bucket.
        """

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str):
        """
        Deletes a file from the specified bucket.
        """
