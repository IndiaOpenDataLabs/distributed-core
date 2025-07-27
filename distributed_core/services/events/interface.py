"""
app/services/events/interface.py

This module defines the interface for event bus services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from distributed_core.core.plugins import define_interface


@define_interface
class EventBusInterface(ABC):
    """
    Interface for event bus services.
    """

    @abstractmethod
    def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publishes a message to a topic.
        """

    @abstractmethod
    def subscribe(self, topic: str, callback):
        """
        Subscribes to a topic and registers a callback.
        """

    @abstractmethod
    def unsubscribe(self, topic: str, callback):
        """
        Unsubscribes a callback from a topic.
        """
