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

# IMPORTANT: Do NOT import app.kafka_producer at module import time here,
# as test collection may import this file as top-level "kafka", and pulling
# app.kafka_producer from here causes a circular import. Instead, provide a
# lazy accessor for app-level helpers.

_kafka_pkg = import_module("kafka")

KafkaProducer = getattr(_kafka_pkg, "KafkaProducer", None)
errors = getattr(_kafka_pkg, "errors", None)
KafkaError = getattr(errors, "KafkaError", None) if errors else None


def _app_helpers():
    """Lazy import app-level producer helpers to avoid circular imports.

    Returns:
        tuple: (KafkaProducerSingleton, publish_product_created,
                publish_product_updated, send_message)
    """
    from app.kafka_producer import (  # local import to break cycle in tests
        KafkaProducerSingleton,
        publish_product_created,
        publish_product_updated,
        send_message,
    )
    return (
        KafkaProducerSingleton,
        publish_product_created,
        publish_product_updated,
        send_message,
    )


def __getattr__(name: str):
    """Support attribute-style access for app helpers on this module.

    Allows: ``from app import kafka as k; k.publish_product_created(...)``
    without importing app helpers at module import time.
    """
    if name in {"KafkaProducerSingleton", "publish_product_created", "publish_product_updated", "send_message"}:
        (KafkaProducerSingleton, publish_product_created, publish_product_updated, send_message) = _app_helpers()
        return {
            "KafkaProducerSingleton": KafkaProducerSingleton,
            "publish_product_created": publish_product_created,
            "publish_product_updated": publish_product_updated,
            "send_message": send_message,
        }[name]
    raise AttributeError(name)


__all__ = [
    "KafkaProducer",
    "KafkaError",
    "KafkaProducerSingleton",
    "publish_product_created",
    "publish_product_updated",
    "send_message",
]
