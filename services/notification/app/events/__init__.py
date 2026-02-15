"""Event processing module for notification service.

This module exports Kafka consumer and event handlers for processing
notification events from the message broker.
"""

from app.events.kafka_consumer import start_consumer, consume_single_message, KafkaConsumerSingleton
from app.events.handlers import handle_event

__all__ = [
    "start_consumer",
    "consume_single_message",
    "KafkaConsumerSingleton",
    "handle_event"
]
