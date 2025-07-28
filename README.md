# distributed-core

A Python library for building powerful, pluggable, and distributed data processing pipelines.

## The Core Idea: Composable Pipelines

`distributed-core` allows you to build complex workflows by assembling independent, reusable components. The core idea is to define a `PipelineContext` that holds all the data for an operation, and then build a `Pipeline` to process it.

The pipeline is a series of stages that can either filter/modify the context (`Execute` plugins) or hand it off to an external system for asynchronous processing (`Dispatch` plugins). This makes your system incredibly flexible, configurable, and easy to test.

## A Practical Example: Asynchronous File Upload

Let's demonstrate the power of this approach with a common use case: creating a FastAPI endpoint that accepts a file, uploads it to a cloud storage service, and then schedules a background task to process it.

### The Goal

We want an endpoint `/upload` that:
1.  Receives binary file content and creates a `FileJobContext`.
2.  Uses an `Execute` plugin (`storage_write`) to save the file to a storage backend.
3.  Uses a `Dispatch` plugin (`schedule_job`) to enqueue the rest of the pipeline for background processing.
4.  Returns a job ID to the client immediately.

### Step 1: Define the Context

The context holds all the data needed for the pipeline.

```python
# app/contexts.py
from fastapi import BackgroundTasks
from distributed_core.core.context import PipelineContext

class FileJobContext(PipelineContext):
    file_path: str
    file_content: bytes
    job_type: str
    background_tasks: BackgroundTasks
```

### Step 2: Define the Stage Interfaces

Interfaces are the contracts for our plugins. The framework provides two: `Execute` for synchronous filters and `Dispatch` for asynchronous hand-offs.

```python
# distributed_core/core/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar
from distributed_core.core.plugins import define_interface
from distributed_core.core.context import PipelineContext

ContextType = TypeVar("ContextType", bound=PipelineContext)

@define_interface
class Execute(ABC):
    """A chainable filter/interceptor that calls `execute(next_fn, context)`."""
    @abstractmethod
    def execute(self, next_fn: Callable, context: ContextType) -> Any:
        ...

@define_interface
class Dispatch(ABC):
    """Hands off the rest of the pipeline for asynchronous execution via `dispatch(next_fn, context)`."""
    @abstractmethod
    def dispatch(self, next_fn: Callable, context: ContextType) -> Any:
        ...
```

### Step 3: Create the Building Blocks (Plugins)

Plugins are concrete implementations of our interfaces. Here, we'd have a `storage_write` plugin implementing `Execute` and a `schedule_job` plugin implementing `Dispatch`.

*(Implementations for `storage_write` and `schedule_job` plugins would be here, registered with `@register_plugin`)*

### Step 4: Assemble and Run the Pipeline

Finally, we assemble the pipeline in our FastAPI application.

```python
# main.py
from fastapi import FastAPI, BackgroundTasks, UploadFile
from typing import Any
from app.contexts import FileJobContext
from distributed_core.core.interfaces import Execute, Dispatch

app = FastAPI()

@app.post("/upload")
async def upload_endpoint(background_tasks: BackgroundTasks, file: UploadFile) -> Any:
    # 1. Build the request-scoped context
    ctx = FileJobContext(
        file_path=f"uploads/{file.filename}",
        file_content=await file.read(),
        job_type="fastapi",
        background_tasks=background_tasks
    )

    # 2. Define the core business logic that runs last (in the background)
    def core_finalize(context: FileJobContext) -> Any:
        print(f"SUCCESS: Background processing for '{context.file_path}' is complete.")
        return {"stored_path": context.file_path, "ok": True}

    # 3. Create a pipeline and chain the stages
    #    Execution order is top-to-bottom.
    pipeline = ctx.create_pipeline(core_fn=core_finalize)
    pipeline.chain(
        Dispatch, plugin="schedule_job"
    ).chain(
        Execute,  plugin="storage_write"
    ).chain(
        Execute,  plugin="logging" # Example of another filter
    )

    # 4. Run the pipeline
    # The 'schedule_job' dispatcher will intercept the call, schedule the rest
    # of the chain to run in the background, and return immediately.
    result = pipeline.run()
    return result
```

This example demonstrates a clean separation of concerns. The endpoint is declarative, simply stating *what* needs to be done, while the underlying plugins handle *how* it gets done. You could swap storage backends or job runners with a one-line configuration change.

## How It Works: Key Concepts

*   **`PipelineContext`**: A Pydantic `BaseModel` that holds all the data for a given operation and can create a `Pipeline`.
*   **`Pipeline`**: The orchestrator. You create it from a context, chain stages, and `run()` it.
*   **`Execute`**: An interface for synchronous, chainable filters. Each `execute` method must call the `next_fn` to continue the pipeline.
*   **`Dispatch`**: An interface for a stage that hands off the remainder of the pipeline for asynchronous execution. Its `dispatch` method schedules the `next_fn` to run in a background process (e.g., using FastAPI's BackgroundTasks or a Celery worker) and typically returns immediately. A pipeline can only have one `Dispatch` stage.
*   **`@define_interface`**: A decorator that marks an abstract class as a contract for plugins.
*   **`@register_plugin`**: A decorator that registers a concrete class as an implementation of an interface, giving it a unique name (e.g., "minio").
*   **`PluginFactory`**: A factory that instantiates plugins on demand. The `Pipeline` uses this to create the stages you chain.

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

*(Note: These services will be adapted to the new Execute/Dispatch plugin model.)*

## Future Features:

### Execution Order Clarification

**Dispatch Behavior:**

The core ambiguity was whether Dispatch terminates or backgrounds the pipeline. Since it backgrounds execution:
```python
pipeline.chain(Dispatch("schedule_job"))  // Backgrounds subsequent stages
        .chain(Execute("storage_write"))   // Runs in background
        .chain(Execute("logging"))         // Runs in background
```
**Recommendation:** Explicitly document that:

- Stages chained after Dispatch run in the background context
- Stages before Dispatch run synchronously

**Pipeline Visualization:**

Add pipeline diagrams showing sync vs async boundaries:
```text
[Sync] → [Dispatch] → |Async Boundary| → [Background Stages]
```

### Enhanced Error Handling Architecture

**Error Propagation:**

Implement pipeline-wide error bus:
```python
class ErrorHandler(Execute):
    def execute(self, next_fn, context):
        try:
            return next_fn(context)
        except Exception as e:
            context.error_bus.report(e)
            raise
```

**Recovery Mechanisms:**

Add `@retry` policy to plugin interfaces:
```python
@define_interface
class Execute(ABC):
    retry_policy: RetryPolicy = RetryPolicy(backoff=1.5, attempts=3)
```

**Dead Letter Queues:**

Integrate with `EventBusInterface` for failed contexts:
```python
class DeadLetterPlugin(Dispatch):
    def dispatch(self, next_fn, context):
        if context.failed:
            self.event_bus.publish("dlq", context)
```

### Concurrency & Resource Management

**Resource Locking:**

Add advisory locking interface:
```python
class LockingPlugin(Execute):
    def execute(self, next_fn, context):
        with self.distributed_lock(context.job_id):
            return next_fn(context)
```
Provide implementations for Redis/DB-based locks

**Lifecycle Hooks:**

Mandate context managers for resource-heavy plugins:
```python
class StorageInterface(Execute):
    def __enter__(self):
        self._connect()
    
    def __exit__(self, *exc):
        self._release()
```

**Connection Pooling:**

Add `PluginPool` factory for stateful resources:
```python
plugin = plugin_pool.acquire(StorageInterface, "minio")
try:
    pipeline.run()
finally:
    plugin_pool.release(plugin)
```

### ⚙️ Type Safety Improvements

**Generic Context Binding:**
```python
T = TypeVar("T", bound=PipelineContext)

class Execute(ABC):
    @abstractmethod
    def execute(self, next_fn: Callable[[T], T], context: T) -> T:
        ...
```

**Context Versioning:**

Add version field to `PipelineContext`:
```python
class PipelineContext(BaseModel):
    __version__: str = "1.0"
```

### Distributed-First Enhancements

**Context Serialization:**

Auto-implement serialization for job queues:
```python
context.model_dump_json()  # For job enqueueing
```

**Sharding Support:**

Add partition keys to context:
```python
class FileJobContext(PipelineContext):
    @property
    def shard_key(self):
        return hash(self.file_path) % 1024
```

**Observability Hooks:**

Integrate OpenTelemetry:
```python
class TracingPlugin(Execute):
    def execute(self, next_fn, context):
        with tracer.start_as_current_span("storage_write"):
            return next_fn(context)
```

### ✅ Recommended Implementation Priorities

**Pipeline Integrity:**

- Enforce stage ordering constraints (e.g., single Dispatch)
- Add pipeline visualizer for debugging

**Error Subsystem:**

- Implement retry policies + dead letter queues
- Standardize error reporting interface

**Concurrency Primitives:**

- Ship with Redis lock implementation
- Add connection pooling reference implementation

**Distributed Testing:**

- Provide simulated distributed environment
- Chaos testing helpers (network partitions, latency injection)

This refined architecture maintains your pluggable design while adding crucial production-grade capabilities. The key evolution is treating pipelines as distributed transactions requiring:

- Atomic execution phases
- Cross-stage error propagation
- Coordinated resource locking
- Observable state transitions

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