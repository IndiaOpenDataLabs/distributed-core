# pylint: disable=R0903
"""
Application Configuration using Pydantic BaseSettings.

This module defines the application's configuration settings, which are loaded
from environment variables. It centralizes configuration management, making it
easy to manage and validate settings.
"""

import importlib

from pydantic_settings import BaseSettings

from distributed_core.core.config_loader import ConfigLoader


class Settings(BaseSettings):
    """
    Defines the application's configuration settings,
    loaded from environment variables.
    """

    # ——— Core settings ———
    LOG_LEVEL: str = "info"

    # ——— Redis settings ———
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ——— MinIO settings ———
    MINIO_HOST: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"

    # ——— Storage settings ———
    STORAGE_SERVICE_TYPE: str = "minio"  # "local" or "minio"
    LOCAL_STORAGE_PATH: str = "./data/local_storage"

    # ——— Config Loader settings ———
    CONFIG_LOADER_CLASS: str = "distributed_core.core.config.DefaultConfigLoader"

    class Config:
        """
        Pydantic settings configuration.
        """

        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


class DefaultConfigLoader(ConfigLoader):
    """
    Default configuration loader that uses Pydantic BaseSettings
    to load settings from environment variables and .env files.
    """

    def get_settings(self) -> Settings:
        """
        Returns an instance of the application settings.
        """
        return Settings()


# Dynamically load the ConfigLoader and get the settings instance
# This allows for pluggable configuration loading mechanisms.
_initial_settings_for_loader_selection = (
    Settings()
)  # Temporarily load to get CONFIG_LOADER_CLASS
CONFIG_LOADER_CLASS_PATH = _initial_settings_for_loader_selection.CONFIG_LOADER_CLASS

# Split path into module and class name
module_name, class_name = CONFIG_LOADER_CLASS_PATH.rsplit(".", 1)

# Dynamically import the module and get the class
module = importlib.import_module(module_name)
ConfigLoaderClass = getattr(module, class_name)

# Instantiate the chosen ConfigLoader and get the settings
config_loader_instance = ConfigLoaderClass()
settings = config_loader_instance.get_settings()
