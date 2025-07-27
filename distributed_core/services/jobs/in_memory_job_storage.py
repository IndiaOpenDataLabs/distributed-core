"""
app/services/in_memory_job_storage.py

This module provides an in-memory implementation of the JobStorage service.
"""

from typing import Any, Dict

from distributed_core.core.plugins import register_plugin
from distributed_core.services.jobs.interface import JobStorageInterface


@register_plugin(JobStorageInterface, name="in-memory")
class InMemoryJobStorage(JobStorageInterface):
    """
    An in-memory implementation of the JobStorage service.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def save_job(
        self,
        job_id: str,
        status: str,
        result: Dict[str, Any] | None = None,
        error: str | None = None,
    ):
        """
        Saves or updates the status and result of a job in memory.
        """
        self._jobs[job_id] = {"status": status, "result": result, "error": error}

    def get_job(self, job_id: str) -> Dict[str, Any] | None:
        """
        Retrieves the status and result of a job from memory.
        """
        return self._jobs.get(job_id)
