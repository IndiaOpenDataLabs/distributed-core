"""
# distributed_core/core/config.py
"""
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Settings for the distributed core module.
    """

    # Define any settings specific to the distributed core here
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

settings = Settings()