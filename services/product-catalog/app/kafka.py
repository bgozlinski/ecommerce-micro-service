"""Compatibility shim to avoid name clash with the external ``kafka`` package.

Why this file exists:
- Some code (or third-party tools) may import ``kafka`` and, due to Python's
  module resolution order while running tests, this local file could be picked
  up instead of the external ``kafka`` package. That used to cause an import
  error (partially initialized module) during test collection.

Fix/approach:
- When this file is imported as ``kafka``, we proxy the symbols from the real
  external package via ``importlib`` so that ``KafkaProducer`` and friends are
  available as expected.
- We also re-export our app-level producer helpers using an absolute import to
  ``app.kafka_producer`` (no relative import), so this module works whether it
  is imported as ``kafka`` or ``app.kafka``.
"""

from importlib import import_module
from app.kafka_producer import (
    KafkaProducerSingleton,
    publish_product_created,
    publish_product_updated,
    send_message,
)

_kafka_pkg = import_module("kafka")

KafkaProducer = getattr(_kafka_pkg, "KafkaProducer", None)
errors = getattr(_kafka_pkg, "errors", None)
KafkaError = getattr(errors, "KafkaError", None) if errors else None

__all__ = [
    "KafkaProducer",
    "KafkaError",
    "KafkaProducerSingleton",
    "publish_product_created",
    "publish_product_updated",
    "send_message",
]
