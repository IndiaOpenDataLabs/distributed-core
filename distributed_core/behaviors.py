# pylint: disable=R0903
"""
distributed_core/behaviors.py

Defines the interface for task behaviors.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable


class Behavior(ABC):
    """
    The interface for a behavior that can be added to a Task.
    """

    def __init__(self, **config: Any):
        self.config = config

    @abstractmethod
    def execute(self, task_func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the behavior's logic and calls the next function in the chain.
        """
        raise NotImplementedError
