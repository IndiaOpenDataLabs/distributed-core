# pylint: disable=R0903
"""
distributed_core/behaviors.py

Defines the interface for task behaviors.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from distributed_core.core.plugins import define_interface

@define_interface
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


# @define_interface
# class Execute(ABC):
#     """A chainable filter/interceptor."""
#     @abstractmethod
#     def execute(self, next_fn: Callable, context: Context) -> Any:
#         ...

# @define_interface
# class Dispatch(ABC):
#     """Terminates the chain by dispatching to an external system."""
#     @abstractmethod
#     def execute(self, next_fn: Callable, context: Context) -> Any:
#         ...

