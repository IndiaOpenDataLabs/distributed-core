# pylint: disable=R0903
"""
app/services/fastapi_background_runner.py

This module provides an implementation of the BackgroundTaskRunner service
using FastAPI's BackgroundTasks.
"""

from typing import Callable

from fastapi import BackgroundTasks

from distributed_core.plugins import register_plugin
from distributed_core.services.jobs.interface import BackgroundTaskRunnerInterface


@register_plugin(BackgroundTaskRunnerInterface, name="fastapi")
class FastAPIBackgroundRunner(BackgroundTaskRunnerInterface):
    """
    An implementation of the BackgroundTaskRunner service using FastAPI's
    BackgroundTasks.
    """

    def __init__(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks

    def submit_task(self, task_function: Callable, *args, **kwargs):
        """
        Submits a function to be run as a background task using FastAPI's
        BackgroundTasks.
        """
        self._background_tasks.add_task(task_function, *args, **kwargs)
