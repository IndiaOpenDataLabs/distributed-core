"""
app/services/jobs/manager.py

This module defines the manager for job-related services.
"""

from distributed_core.services.jobs.base import BackgroundTaskRunner, JobStorage
from distributed_core.services.jobs.fastapi_background_runner import (
    FastAPIBackgroundRunner,
)
from distributed_core.services.jobs.redis_job_storage import RedisJobStorage


class JobManager:
    """
    Manages and provides access to job-related services.
    """

    _job_storage: JobStorage | None = None
    _background_task_runner: BackgroundTaskRunner | None = None

    @classmethod
    def get_job_storage(cls) -> JobStorage:
        """
        Returns the configured JobStorage instance.
        For now, it returns a RedisJobStorage instance.
        """
        if cls._job_storage is None:
            # Use RedisJobStorage for shared state across workers
            cls._job_storage = RedisJobStorage()
        return cls._job_storage

    @classmethod
    def get_background_task_runner(cls, background_tasks) -> BackgroundTaskRunner:
        """
        Returns the configured BackgroundTaskRunner instance.
        For now, it returns a FastAPIBackgroundRunner instance.
        """
        if cls._background_task_runner is None:
            cls._background_task_runner = FastAPIBackgroundRunner(background_tasks)
        return cls._background_task_runner
