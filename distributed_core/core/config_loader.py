"""
app/core/config_loader.py

This module defines the base class for configuration loaders.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# Only import Settings for type checking purposes to avoid circular dependency
if TYPE_CHECKING:
    from distributed_core.core.config import Settings


class ConfigLoader(ABC):
    """
    Abstract Base Class for configuration loaders.
    Defines the interface for how application settings are loaded.
    """

    @abstractmethod
    def get_settings(self) -> "Settings":
        """
        Abstract method to retrieve application settings.
        Concrete implementations must provide their own logic for loading settings.
        """
