"""
distributed_core/tasks.py

The primary user-facing API for creating and managing distributed tasks.
"""
from functools import wraps
from typing import Any, Callable, Type

from distributed_core.behaviors import Behavior
from distributed_core.plugins import PluginFactory


class Task:
    """
    A wrapper for a function that can be enhanced with various behaviors.
    """

    def __init__(self, func: Callable):
        self._func = func
        self.submit = func  # Start with the original function

    def add_behavior(
        self,
        behavior_interface: Type[Behavior],
        *,
        plugin: str,
        **config: Any,
    ) -> "Task":
        """
        Adds a behavior to the task by wrapping the current `submit` method.
        """
        # Get the behavior's implementation class from the plugin registry
        behavior_class = PluginFactory.get(behavior_interface, name=plugin)
        # Instantiate the behavior with its specific configuration
        behavior_instance = behavior_class(**config)

        # The current submit function becomes the next link in the chain
        next_func_in_chain = self.submit

        # Create the new wrapper
        @wraps(next_func_in_chain)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Call the behavior's execute method, passing it the next function
            return behavior_instance.execute(next_func_in_chain, *args, **kwargs)

        # The new wrapper becomes the current submit method
        self.submit = wrapper
        return self
