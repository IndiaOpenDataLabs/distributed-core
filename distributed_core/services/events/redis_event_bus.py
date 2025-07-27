"""
app/services/events/redis_event_bus.py

This module provides a Redis Pub/Sub implementation of the EventBus service.
"""

import json
from typing import Any, Callable, Dict
import logging

import redis

from distributed_core.core.config import settings
from distributed_core.plugins import register_plugin
from distributed_core.services.events.interface import EventBusInterface

logger = logging.getLogger(__name__)


@register_plugin(EventBusInterface, name="redis")
class RedisEventBus(EventBusInterface):
    """
    A Redis Pub/Sub implementation of the EventBus service.
    """

    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publishes a message to a specified Redis channel.
        """
        self._redis.publish(topic, json.dumps(message))

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribes a handler function to a specified Redis topic.

        Note: This is a blocking operation and typically runs in a
        separate thread/process.
        """
        pubsub = self._redis.pubsub()
        pubsub.subscribe(topic)
        logger.info("Subscribed to topic: %s", topic)
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                callback(data)

    def unsubscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Unsubscribe a previously registered callback from a Redis topic.
        """
        pubsub = self._redis.pubsub()
        pubsub.unsubscribe(topic)
        logger.info("Unsubscribed from channel: %s", topic)
