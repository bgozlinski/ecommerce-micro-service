"""Backward-compatibility shim for product Kafka producer.

This module re-exports public symbols from ``app.kafka_producer``. It exists to
avoid circular import issues with the external ``kafka`` package when tests or
legacy imports reference ``app.kafka``.
"""

from .kafka_producer import (  # noqa: F401
    KafkaProducerSingleton,
    publish_product_created,
    publish_product_updated,
    send_message,
)
