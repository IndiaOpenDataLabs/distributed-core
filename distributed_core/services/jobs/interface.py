# pylint: disable=R0903
"""
app/services/jobs/interface.py

This module defines the interfaces for job-related services.
"""

from abc import abstractmethod
from typing import Any, Callable, Dict

from distributed_core.core.plugins import define_interface


@define_interface
class JobStorageInterface:
    """
    Interface for job storage services.
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


@define_interface
class BackgroundTaskRunnerInterface:
    """
    Interface for background task execution services.
    """

    @abstractmethod
    def submit_task(self, task_function: Callable, *args, **kwargs):
        """
        Submits a function to be run as a background task.
        """
