"""
app/services/redis_job_storage.py

This module provides a Redis-backed implementation of the JobStorage service.
"""

import json
from typing import Any, Dict

import redis

from distributed_core.core.config import settings  # Import settings
from distributed_core.services.jobs.base import JobStorage


class RedisJobStorage(JobStorage):
    """
    A Redis-backed implementation of the JobStorage service.
    """

    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def save_job(
        self,
        job_id: str,
        status: str,
        result: Dict[str, Any] | None = None,
        error: str | None = None,
    ):
        """
        Saves or updates the status and result of a job in Redis.
        """
        job_data = {"status": status, "result": result, "error": error}
        self._redis.set(f"job:{job_id}", json.dumps(job_data))

    def get_job(self, job_id: str) -> Dict[str, Any] | None:
        """
        Retrieves the status and result of a job from Redis.
        """
        job_data_json = self._redis.get(f"job:{job_id}")
        if job_data_json:
            return json.loads(job_data_json)
        return None
