# # Decorator helpers

# from functools import wraps
# from typing import Any, Callable
# from distributed_core.tasks import Task
# from distributed_core.core.behaviors import Behavior


# def background(job_type: str, **config: Any):
#     """
#     Decorator to schedule a function call inside a background job.
#     Usage:
#         @background("celery")
#         def process(path: str):
#             return {"done": path}
#     """
#     def decorator(func: Callable):
#         @wraps(func)
#         def wrapper(*args: Any, **kwargs: Any) -> Any:
#             task = Task(func)
#             task.add_behavior(Behavior, plugin="schedule_job", job_type=job_type, **config)
#             return task.submit(*args, **kwargs)
#         return wrapper
#     return decorator