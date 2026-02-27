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

# Proxy to the real external package "kafka" so that imports like
# ``from kafka import KafkaProducer`` work even if this file is resolved.
_kafka_pkg = import_module("kafka")

# Re-export commonly used external symbols (add more if ever needed)
KafkaProducer = getattr(_kafka_pkg, "KafkaProducer", None)
errors = getattr(_kafka_pkg, "errors", None)
KafkaError = getattr(errors, "KafkaError", None) if errors else None

# Re-export our application producer helpers using ABSOLUTE import to avoid
# relative import failures when this module is imported as top-level "kafka".
from app.kafka_producer import (  # type: ignore F401
    KafkaProducerSingleton,
    publish_product_created,
    publish_product_updated,
    send_message,
)

__all__ = [
    # External
    "KafkaProducer",
    "KafkaError",
    # App helpers
    "KafkaProducerSingleton",
    "publish_product_created",
    "publish_product_updated",
    "send_message",
]
