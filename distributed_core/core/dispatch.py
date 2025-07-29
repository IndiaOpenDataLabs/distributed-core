# pylint: disable=R0903
"""
distributed_core/core/dispatch.py

Defines the interface for execute behaviors.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from distributed_core.core.plugins import define_interface
from distributed_core.core.context import TaskContext

@define_interface
class Dispatch(ABC):
    """
    Dispatches the chain for execution to an external system.
    """

    def __init__(self, **config: Any):
        self.config = config

    @abstractmethod
    def dispatch(self, next_fn: Callable,  context: TaskContext) -> Any:
        """
        Abstract method to dispatch to an external system
        """
        raise NotImplementedError
