"""
app/services/events/redis_event_bus.py

This module provides a Redis Pub/Sub implementation of the EventBus service.
"""

import json
import logging
from typing import Any, Callable, Dict

import redis

from distributed_core.core.config import settings
from distributed_core.services.events.base import EventBus

logger = logging.getLogger(__name__)


class RedisEventBus(EventBus):
    """
    A Redis Pub/Sub implementation of the EventBus service.
    """

    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def publish(self, channel: str, message: Dict[str, Any]):
        """
        Publishes a message to a specified Redis channel.
        """
        self._redis.publish(channel, json.dumps(message))

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribes a handler function to a specified Redis channel.

        Note: This is a blocking operation and typically runs in a
        separate thread/process.
        """
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)
        logger.info("Subscribed to channel: %s", channel)
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                handler(data)
