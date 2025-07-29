# pipeline.py
from functools import wraps
from typing import Any, Callable, List, Type

from distributed_core.core.plugins import PluginFactory
from distributed_core.core.execute import Execute
from distributed_core.core.dispatch import Dispatch

class Pipeline:
    """
    Orchestrates a context through a series of chained filters (Execute)
    and an optional final handoff (Dispatch). Filters call `execute(...)` and
    the handoff calls `dispatch(...)`. Behaviors execute in the order chained.
    """

    def __init__(self, context: Any):
        # The data container (Pydantic BaseModel, dict, etc.)
        self.context = context
        # The core function to call after middleware (must be set)
        self._func: Callable[[Any], Any] | None = None
        # Preserves middleware behaviors in chain order
        self._middlewares: List[Execute] = []
        # At most one Dispatch
        self._terminator: Dispatch | None = None

    def set_core(self, func: Callable[[Any], Any]) -> "Pipeline":
        """
        Define the core function to execute at the end of the middleware chain.
        :param func: Callable that accepts the context and returns the final result
        """
        self._func = func
        return self

    def chain(
        self,
        behavior_interface: Type[Any],
        *,
        plugin: str,
        **config: Any,
    ) -> "Pipeline":
        """
        Add a filter or handoff stage to the pipeline.

        :param behavior_interface: Execute or Dispatch
        :param plugin: name of the registered plugin
        :param config: passed to the plugin constructor
        """
        beh = PluginFactory.get(behavior_interface, plugin, **config)
        if isinstance(beh, Dispatch):
            if self._terminator is not None:
                raise RuntimeError("Only one Dispatch allowed")
            self._terminator = beh
        else:
            self._middlewares.append(beh)
        return self

    def run(self) -> Any:
        """
        Execute the pipeline: run all filters (calling `execute(fn, ctx)`),
        then either handoff via `dispatch(fn, ctx)` or call the core function directly.

        :return: The result of the handoff dispatch or core function
        """
        if self._func is None:
            raise RuntimeError("Core function not set; call set_core() before run().")

        # Build nested middleware wrappers so that first chained runs first
        next_fn: Callable = self._func
        for middleware in reversed(self._middlewares):
            current_fn = next_fn
            def make_wrapper(mw, fn):
                @wraps(fn)
                def wrapper(ctx):
                    return mw.execute(fn, ctx)
                return wrapper
            next_fn = make_wrapper(middleware, current_fn)

        # Invoke handoff or core
        if self._terminator:
            return self._terminator.dispatch(next_fn, self.context)
        return next_fn(self.context)
    


# pipeline = Pipeline(ctx)
# pipeline.set_core(core_fn) \
#         .chain(Dispatch,  plugin="schedule_job") \
#         .chain(Execute, plugin="storage_write") \
#         .chain(Execute, plugin="logging")
# result = pipeline.run()