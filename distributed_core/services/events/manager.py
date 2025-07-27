# pylint: disable=R0903
"""
app/services/events/manager.py

This module defines the manager for event-related services.
"""

from distributed_core.services.events.base import EventBus
from distributed_core.services.events.redis_event_bus import RedisEventBus


class EventManager:
    """
    Manages and provides access to event-related services.
    """

    _event_bus: EventBus | None = None

    @classmethod
    def get_event_bus(cls) -> EventBus:
        """
        Returns the configured EventBus instance.
        For now, it returns a RedisEventBus instance.
        """
        if cls._event_bus is None:
            cls._event_bus = RedisEventBus()
        return cls._event_bus
