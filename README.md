# distributed-core

A Python library for building powerful, pluggable, and distributed data processing pipelines.

## The Core Idea: Composable Pipelines

`distributed-core` allows you to build complex workflows by assembling independent, reusable components. The core idea is to break down a large process into a series of "behaviors" that can be chained together to form a `Task`.

Each behavior is powered by a pluggable backend. For example, a `storage` behavior can use a `minio` plugin for cloud storage or a `local` plugin for filesystem storage, without changing your application code. This makes your system incredibly flexible, configurable, and easy to test.

## A Practical Example: Asynchronous File Upload

Let's demonstrate the power of this approach with a common use case: creating a FastAPI endpoint that accepts a file, uploads it to a cloud storage service (MinIO), and then schedules a background task to process it.

### The Goal

We want an endpoint `/upload` that:
1.  Receives binary file content.
2.  Uses a `storage_write` behavior to save the file to MinIO.
3.  Uses a `schedule_job` behavior to enqueue the next processing step as a background job.
4.  Returns a job ID to the client immediately.

### Step 1: Define the Contracts (Interfaces)

Interfaces are abstract base classes that define what a certain type of plugin can do.

```python
# distributed_core/services/jobs/interface.py
from abc import ABC, abstractmethod
from typing import Callable, Any
from distributed_core.core.plugins import define_interface

@define_interface
class JobInterface(ABC):
    """
    Interface for scheduling a callable to run asynchronously.
    """
    @abstractmethod
    def schedule(self, fn: Callable, *args: Any, **kwargs: Any) -> str:
        """
        Schedule `fn(*args, **kwargs)` to run later.
        Returns a job_id.
        """
        ...
```

```python
# distributed_core/services/storage/interface.py
from abc import ABC, abstractmethod
from distributed_core.core.plugins import define_interface

@define_interface
class StorageInterface(ABC):
    @abstractmethod
    def write_file(self, path: str, data: bytes) -> None:
        ...

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        ...
```

### Step 2: Create the Building Blocks (Plugins)

Plugins are concrete implementations of our interfaces. Here, we implement a job scheduler using FastAPI's `BackgroundTasks` and a storage backend using MinIO.

```python
# distributed_core/services/jobs/fastapi_background_runner.py
import uuid
from typing import Callable, Any
from fastapi import BackgroundTasks
from distributed_core.core.plugins import register_plugin
from distributed_core.services.jobs.interface import JobInterface

@register_plugin(JobInterface, name="fastapi")
class FastAPIJob(JobInterface):
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def schedule(self, fn: Callable, *args: Any, **kwargs: Any) -> str:
        job_id = str(uuid.uuid4())
        self.background_tasks.add_task(fn, *args, **kwargs)
        return job_id
```

```python
# distributed_core/services/storage/minio_storage.py
from distributed_core.core.plugins import register_plugin
from distributed_core.services.storage.interface import StorageInterface
# Assume Minio client is installed and configured
# from minio import Minio

@register_plugin(StorageInterface, name="minio")
class MinioStorage(StorageInterface):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        # In a real implementation, you would initialize the MinIO client here
        # self.client = Minio(...)
        # self.bucket = bucket
        print(f"INFO: MinIO client configured for bucket '{bucket}'.")

    def write_file(self, path: str, data: bytes) -> None:
        # In a real implementation, you would upload to MinIO here
        print(f"INFO: Writing {len(data)} bytes to MinIO at path '{path}'.")
        pass

    def read_file(self, path: str) -> bytes:
        # In a real implementation, you would download from MinIO here
        print(f"INFO: Reading from MinIO at path '{path}'.")
        return b"dummy file content"
```

### Step 3: Define the Pipeline Steps (Behaviors)

Behaviors are special plugins that orchestrate other plugins and control the flow of a task. They use `PluginFactory` to get the specific implementation (`minio`, `fastapi`, etc.) requested at runtime.

```python
# distributed_core/core/behaviors.py (Illustrative implementations)
from typing import Any, Callable
from distributed_core.core.plugins import register_plugin, PluginFactory
from distributed_core.core.behaviors import Behavior
from distributed_core.services.jobs.interface import JobInterface
from distributed_core.services.storage.interface import StorageInterface

@register_plugin(Behavior, name="schedule_job")
class ScheduleJobBehavior(Behavior):
    def execute(self, next_fn: Callable, *args: Any, **kwargs: Any) -> Any:
        # Get job_type from config, default to "fastapi"
        job_type = self.config.pop("job_type", "fastapi")
        # Instantiate the chosen scheduler plugin (e.g., "fastapi")
        scheduler: JobInterface = PluginFactory.get(
            JobInterface,
            job_type,
            **self.config
        )
        # Schedule the remainder of the chain to run in the background
        job_id = scheduler.schedule(next_fn, *args, **kwargs)
        # Return scheduling info immediately
        return {"scheduled": True, "job_id": job_id}

@register_plugin(Behavior, name="storage_write")
class StorageWriteBehavior(Behavior):
    def execute(self, next_fn: Callable, path: str, data: bytes, **kwargs: Any) -> Any:
        # Get backend from config
        backend_name = self.config.pop("backend")
        # Instantiate the storage backend plugin (e.g., "minio")
        backend: StorageInterface = PluginFactory.get(
            StorageInterface,
            backend_name,
            **self.config
        )
        # Perform the write operation
        backend.write_file(path, data)
        # Pass the file path downstream to the next behavior in the chain
        return next_fn(path=path, **kwargs)
```

### Step 4: Assemble and Run the Pipeline

Finally, we assemble the pipeline in our FastAPI application. We create a `Task` and chain the behaviors we need, providing configuration directly.

```python
# main.py
from fastapi import FastAPI, BackgroundTasks
from typing import Any
from distributed_core.core.tasks import Task
from distributed_core.core.behaviors import Behavior

# Assume the plugins and behaviors from previous steps are loaded
# In a real app, these would be in their own modules and imported.

app = FastAPI()

@app.post("/upload")
def upload_endpoint(background_tasks: BackgroundTasks, file_content: bytes) -> Any:
    # This is the core business logic that runs last, in the background.
    def core_finalize(path: str) -> Any:
        print(f"SUCCESS: Background processing for '{path}' is complete.")
        return {"stored_path": path}

    # 1. Wrap the core logic in a Task
    task = Task(core_finalize)

    # 2. Add behaviors to form the pipeline.
    #    Execution order is top-to-bottom.
    task.add_behavior(
        Behavior,
        plugin="storage_write", # Use the StorageWriteBehavior
        backend="minio",        # Configure it to use the "minio" plugin
        endpoint="MINIO_ENDPOINT",
        access_key="MINIO_ACCESS",
        secret_key="MINIO_SECRET",
        bucket="my-bucket"
    ).add_behavior(
        Behavior,
        plugin="schedule_job",   # Use the ScheduleJobBehavior
        job_type="fastapi",      # Configure it to use the "fastapi" plugin
        background_tasks=background_tasks
    )

    # 3. Kick off the chain by submitting the initial arguments.
    #    The arguments `path` and `data` are for the first behavior (storage_write).
    return task.submit(path="uploads/file.bin", data=file_content)
```

This example demonstrates a clean separation of concerns. The endpoint is declarative, simply stating *what* needs to be done (`storage_write`, `schedule_job`), while the underlying plugins handle *how* it gets done. You could swap `minio` for `local` storage or `fastapi` for a `celery` job runner with a one-line configuration change.

## How It Works: Key Concepts

*   **`@define_interface`**: A decorator that marks an abstract class as a contract for plugins.
*   **`@register_plugin`**: A decorator that registers a concrete class as an implementation of an interface, giving it a unique name (e.g., "minio").
*   **`Behavior`**: A special type of plugin that can be chained together. Its `execute` method always receives `next_fn`, a callable representing the next step in the chain.
*   **`Task`**: The orchestrator. You initialize it with your final business logic and then use `.add_behavior()` to build the execution pipeline.
*   **`PluginFactory`**: A factory that instantiates plugins on demand. Behaviors use `PluginFactory.get(Interface, "plugin_name", **config)` to create instances of the plugins they need.

## 🚀 Installation

This library is intended to be installed as a dependency in your Python projects.

```bash
pip install .
```

## 🛠️ Core Services

`distributed-core` comes with several pre-built interfaces and plugins for common distributed system patterns:

*   **Storage**: `StorageInterface` with `minio` and `local_file_storage` implementations.
*   **Events**: `EventBusInterface` with a `redis` implementation for pub/sub messaging.
*   **Jobs**: `JobInterface` and `JobStorageInterface` with `fastapi`, `in_memory`, and `redis` implementations.

## 🧑‍💻 Development

To set up a local development environment, you will need Docker and Docker Compose to run dependent services like Redis and MinIO.

An example `docker-compose.yml` for development:

```yaml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: quay.io/minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

volumes:
  redis_data:
  minio_data:
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.