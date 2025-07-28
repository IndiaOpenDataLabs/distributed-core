# tasks.py
from functools import wraps
from typing import Any, Callable, List, Type

from distributed_core.core.plugins import PluginFactory
from distributed_core.core.behaviors import Behavior

class Task:
    """
    Wraps a user function so you can enhance it with one or more behaviors.
    Behaviors execute in the order they are added.
    """

    def __init__(self, func: Callable):
        # The core function to be called at the end of the behavior chain
        self._func = func
        # List of behavior instances, preserving addition order
        self._behaviors: List[Behavior] = []

    def add_behavior(
        self,
        behavior_interface: Type[Behavior],
        *,
        plugin: str,
        **config: Any,
    ) -> "Task":
        """
        Register a new behavior to run around the core function.

        Behaviors will execute in the exact order they are added.

        :param behavior_interface: The Behavior interface class
        :param plugin: Name of the registered Behavior plugin
        :param config: Configuration passed to the Behavior constructor
        :return: self, for chaining
        """
        # Instantiate the behavior plugin
        behavior_instance = PluginFactory.get(behavior_interface, plugin, **config)
        # Append to the behavior list
        self._behaviors.append(behavior_instance)
        return self

    def submit(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the core function wrapped by all added behaviors.
        Behaviors are invoked in the order they were registered.

        :param args: Positional arguments for the first behavior/core
        :param kwargs: Keyword arguments for the first behavior/core
        :return: The result of the core function
        """
        # Start with the core function
        next_fn: Callable = self._func

        # Wrap each behavior around next_fn, in reverse registration order,
        # so that the first added behavior runs first.
        for behavior in reversed(self._behaviors):
            current_next = next_fn
            # Create a closure that binds the current behavior and next function
            def make_wrapper(beh, nxt):
                @wraps(nxt)
                def wrapper(*a: Any, **kw: Any) -> Any:
                    # Each behavior decides when to call the next layer
                    return beh.execute(nxt, *a, **kw)
                return wrapper

            # Update next_fn to be the new wrapped function
            next_fn = make_wrapper(behavior, current_next)

        # Call the fully-wrapped function chain
        return next_fn(*args, **kwargs)
