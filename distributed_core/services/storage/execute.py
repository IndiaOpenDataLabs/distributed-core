# Decorator helpers

from functools import wraps
from typing import Any, Callable
from distributed_core.core.pipeline import Pipeline
from distributed_core.core.execute import Execute
from distributed_core.core.plugins import register_plugin
from distributed_core.core.context import TaskContext

class FileContext(TaskContext):
    content: bytes
    filename: str
    processed: bool = False

@register_plugin
class Archiver(Execute):
    def execute(self, next_fn, context: FileContext):
        save_to_cloud_storage(context.filename, context.content)
        return next_fn(context)
