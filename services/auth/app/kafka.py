"""Kafka producer for auth-related events.

This module provides a singleton Kafka producer and helper function for
publishing user lifecycle events (user_registered) to the message broker
for consumption by Notification and other services.
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError

import json
import logging
from typing import Optional
from .core.config import settings
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class KafkaProducerSingleton:
    _instance: Optional[KafkaProducer] = None

    @classmethod
    def get_instance(cls) -> KafkaProducer:
        if cls._instance is None:
            logger.info("Tworzę nową instancję Kafka Producer")

            cls._instance = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1,
                compression_type='gzip',
                request_timeout_ms=30000,
            )

        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance:
            logger.info("Zamykam KafkaProducer")
            cls._instance.flush()
            cls._instance.close()
            cls._instance = None
            logger.info("KafkaProducer zamknięty")


def send_message(topic: str, payload: dict, key: Optional[str] = None):
    """Send a message to a Kafka topic.

    Args:
        topic: Kafka topic name.
        payload: Message payload (will be JSON-serialized).
        key: Optional message key for partitioning.

    Raises:
        KafkaError: If message delivery fails.
    """
    try:
        producer = KafkaProducerSingleton.get_instance()
        future = producer.send(topic, value=payload, key=key)
        record_metadata = future.get(timeout=10)
        logger.info(f"Sent message to topic {record_metadata.topic} partition [{record_metadata.partition}] @ offset {record_metadata.offset}")
    except KafkaError as e:
        logger.error(f"Error sending message: {e}")


def publish_user_registered(user_id: int, email: str):
    """Publish a user_registered event to Kafka.

    Args:
        user_id: Newly registered user's ID.
        email: Newly registered user's email.
    """
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": "user_registered",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "userId": user_id,
            "email": email
        }
    }
    send_message(settings.KAFKA_TOPIC_USERS, event, key=str(user_id))
