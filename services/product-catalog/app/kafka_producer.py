"""Kafka producer for product-related events.

This module provides a singleton Kafka producer and helper functions for
publishing product lifecycle events (created, updated) to the message broker
for consumption by Notification and Reporting services.

Important: Avoid top-level imports from the external ``kafka`` package to
prevent import-time name clashes during tests. We lazy-import the package
inside ``get_instance`` instead.
"""

import json
import logging
from typing import Optional, Any
from importlib import import_module
from .core.config import settings
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class KafkaProducerSingleton:
    _instance: Optional[Any] = None

    @classmethod
    def get_instance(cls) -> Any:
        if cls._instance is None:
            logger.info("Tworzę nową instancję Kafka Producer")

            kafka_pkg = import_module("kafka")
            KafkaProducer = getattr(kafka_pkg, "KafkaProducer")

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
        logger.info(
            f"Sent message to topic {record_metadata.topic} partition [{record_metadata.partition}] @ offset {record_metadata.offset}"
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")


def publish_product_created(product_id: int, name: str, price_cents: int):
    """Publish a product_created event to Kafka.

    Args:
        product_id: Product identifier.
        name: Product name.
        price_cents: Product price in cents.
    """
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": "product_created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "productId": product_id,
            "name": name,
            "price": price_cents,
        },
    }
    send_message(settings.KAFKA_TOPIC_PRODUCTS, event, key=str(product_id))


def publish_product_updated(product_id: int, changes: dict):
    """Publish a product_updated event to Kafka.

    Args:
        product_id: Product identifier.
        changes: Dictionary of changed fields.
    """
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": "product_updated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "productId": product_id,
            "changes": changes,
        },
    }
    send_message(settings.KAFKA_TOPIC_PRODUCTS, event, key=str(product_id))
