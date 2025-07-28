# # Decorator helpers

# from functools import wraps
# from typing import Any, Callable
# from distributed_core.tasks import Task
# from distributed_core.core.behaviors import Behavior


# def storage(plugin: str, **config: Any):
#     """
#     Decorator to add a storage behavior to a function.
#     Usage:
#         @storage("minio", endpoint="...", bucket="my-bucket", access_key="...", secret_key="...")
#         def upload_file(path: str, data: bytes):
#             return {"path": path}
#     """
#     def decorator(func: Callable):
#         @wraps(func)
#         def wrapper(*args: Any, **kwargs: Any) -> Any:
#             task = Task(func)
#             task.add_behavior(Behavior, plugin=plugin, **config)
#             return task.submit(*args, **kwargs)
#         return wrapper
#     return decorator