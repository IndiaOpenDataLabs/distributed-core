# core/contexts.py
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar
from pydantic import BaseModel
from distributed_core.tasks import Task

C = TypeVar("C", bound="TaskContext")

class TaskContext(BaseModel, ABC):
    """
    Any Pydantic context that can spawn a Task.
    """

    @abstractmethod
    def create_task(
        self: C,
        core_fn: Callable[[C], Any] | None = None
    ) -> Task:
        ...

    def create_task(self: C, core_fn=None) -> Task:
        # default core just returns the context dict (or add a status field)
        def result(ctx: C):
            return ctx.dict()
        fn = core_fn or result
        from distributed_core.core.behaviors import Behavior
        return Task(fn, self)
    

# # app/contexts.py
# class FileJobContext(TaskContext):
#     file_path:    str
#     file_content: bytes
#     job_id:       str | None = None
#     stored_path:  str | None = None

# ctx = FileJobContext(file_path="…", file_content=b"…")
# pipeline = ctx.create_pipeline()                # uses default core (returns ctx.dict())
# # or
# def finalize(ctx):                       # custom core
#     return {"ok": True, **ctx.dict()}
# task = ctx.create_pipeline(core_fn=finalize)
