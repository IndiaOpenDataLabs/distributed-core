# pylint: disable=R0903
"""
app/services/jobs/base.py

This module defines the base classes for job storage and background
task execution services.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class JobStorage(ABC):
    """
    Base class for job storage services.
    """

    @abstractmethod
    def save_job(
        self,
        job_id: str,
        status: str,
        result: Dict[str, Any] | None = None,
        error: str | None = None,
    ):
        """
        Saves or updates the status and result of a job.
        """

    @abstractmethod
    def get_job(self, job_id: str) -> Dict[str, Any] | None:
        """
        Retrieves the status and result of a job.
        """


class BackgroundTaskRunner(ABC):
    """
    Base class for background task execution services.
    """

    @abstractmethod
    def submit_task(self, task_function: Callable, *args, **kwargs):
        """
        Submits a function to be run as a background task.
        """
