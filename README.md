# distributed-core

A Python library providing core distributed system patterns and utilities for building scalable and resilient applications.

This library encapsulates common functionalities such as pluggable storage, event management, and background job handling, designed to be easily integrated and extended.

## ✨ Features

*   **Pluggable Storage:** Abstracted storage interface with concrete implementations for MinIO/S3-compatible object storage and local filesystem storage.
*   **Event Bus:** A simple event bus abstraction with a Redis Pub/Sub implementation, enabling decoupled communication between services.
*   **Background Job Management:** Base classes and managers for handling background tasks, designed to be extensible for integration with robust job queues like Celery or RQ.
*   **Generic Ingestion Utilities:** Common functions for processing document content (e.g., extracting text from `BytesIO` streams), making ingestion pipelines flexible.
*   **Centralized Configuration:** A robust configuration loading mechanism using Pydantic settings, allowing for easy management via environment variables.

## 🚀 Installation

This library is intended to be installed as a dependency in your Python projects.

```bash
pip install distributed-core # (Future: Once published to PyPI)
```

For now, you can install it from source or include it as a local package in your project.

## 🛠️ Usage

### Configuration

Configuration is managed via environment variables or a `.env` file. Key settings include:

*   **`STORAGE_SERVICE_TYPE`**: `minio` (default) or `local`
*   **`LOCAL_STORAGE_PATH`**: Path for local storage (if `STORAGE_SERVICE_TYPE=local`)
*   **`MINIO_HOST`**, **`MINIO_ACCESS_KEY`**, **`MINIO_SECRET_KEY`**: MinIO connection details
*   **`REDIS_HOST`**, **`REDIS_PORT`**, **`REDIS_DB`**: Redis connection details for Event Bus and Job Storage

### Storage Example

```python
from distributed_core.services.storage.manager import StorageManager
from distributed_core.core.config import settings
from io import BytesIO

# Ensure settings are loaded (e.g., via environment variables or .env file)
# settings = Settings() # If not already loaded by your app

storage_service = StorageManager.get_storage_service()
bucket_name = settings.INGESTION_BUCKET_NAME
object_name = "my-document-123.pdf"
file_content = BytesIO(b"This is some document content.")

# Upload a file
storage_service.upload_file(bucket_name, object_name, file_content, len(file_content.getvalue()))

# Download a file
downloaded_content = storage_service.download_file(bucket_name, object_name)
print(f"Downloaded: {downloaded_content[:50]}...")

# Delete a file
storage_service.delete_file(bucket_name, object_name)
```

### Event Bus Example

```python
from distributed_core.services.events.manager import EventManager

event_bus = EventManager.get_event_bus()

def my_handler(message):
    print(f"Received message: {message}")

# Subscribe to a channel (typically in a separate thread/process)
# event_bus.subscribe("my_channel", my_handler)

# Publish a message
event_bus.publish("my_channel", {"event_type": "data_processed", "data_id": "abc"})
```

### Common Ingestion Example

```python
from distributed_core.services.ingestion.file_common import ingest_file_common
from io import BytesIO

class MyCustomIngestionService:
    def _extract_text(self, document: dict) -> str:
        file_content = document.get("content")
        if not file_content:
            raise ValueError("No content provided.")
        return file_content.read().decode("utf-8") # Simple text extraction

    def ingest(self, document: dict) -> dict:
        return ingest_file_common(
            document,
            service_name="my_custom_ingester",
            version="1.0.0",
            extract_text_func=self._extract_text
        )

# Example usage
doc_data = {
    "content": BytesIO(b"Hello, this is a test document."),
    "source": "test-doc-1.txt",
    "original_filename": "test.txt"
}

my_ingester = MyCustomIngestionService()
result = my_ingester.ingest(doc_data)
print(result)
```

## 🧑‍💻 Development

To set up a local development environment for `distributed-core` and test its functionalities, you will typically need:

*   **Docker & Docker Compose:** To run dependent services like Redis and MinIO.

An example `docker-compose.yml` for development might look like:

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

Contributions are welcome! Please refer to the project's contribution guidelines (if any) for details on how to get involved.
