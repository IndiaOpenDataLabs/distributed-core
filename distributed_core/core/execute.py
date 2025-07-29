# pylint: disable=R0903
"""
distributed_core/core/execute.py

Defines the interface for execute behaviors.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from distributed_core.core.plugins import define_interface
from distributed_core.core.context import TaskContext

@define_interface
class Execute(ABC):
    """
    A chainable filter/interceptor.
    """

    def __init__(self, **config: Any):
        self.config = config

    @abstractmethod
    def execute(self, next_fn: Callable, context: TaskContext) -> Any:
        """
        Abstract method to call next_fn
        """
        raise NotImplementedError
