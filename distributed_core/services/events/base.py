"""
app/services/events/base.py

This module defines the base classes for event bus services.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class EventBus(ABC):
    """
    Base class for event bus services.
    """

    @abstractmethod
    def publish(self, channel: str, message: Dict[str, Any]):
        """
        Publishes a message to a specified channel.
        """

    @abstractmethod
    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribes a handler function to a specified channel.

        Note: In a real-world scenario, subscription often involves
        long-running processes.
        """
