from kafka import KafkaProducer
from kafka.errors import KafkaError

import json
import logging
from typing import Any, Optional
from .core.config import settings
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class KafkaProducerSingleton:
    """
    Tworzymy jeden producer na całą palikacje (thread-safe)

    """
    _instance: Optional[KafkaProducer] = None

    @classmethod
    def get_instance(cls) -> KafkaProducer:
        if cls._instance is None:
            logger.info("Tworzę nową instancje Kafka Producer")

            cls._instance = KafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                                          value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                          key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                                          acks='all',
                                          retries=3,
                                          max_in_flight_requests_per_connection=1,
                                          compression_type='gzip',
                                          request_timeout_ms=30000, # 30s timeout
                                          )

        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance:
            logger.info("Zamykam KafkaProducer")
            cls._instance.flush()
            cls._instance.close()
            cls._instance = None
            logger.info("KafkaPoroducer zamknięty")



def send_message(topic: str, payload: dict, key: Optional[str] = None):
    try:
        producer = KafkaProducerSingleton.get_instance()
        future = producer.send(topic, value=payload, key=key)
        record_metadata = future.get(timeout=10)
        logger.info(f"Sent message to topic {record_metadata.topic} partition [{record_metadata.partition}] @ offset {record_metadata.offset}")
    except KafkaError as e:
        logger.error(f"Error sending message: {e}")

def publish_order_event(event_type: str, order_id: int, user_id: int, payload: dict):
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "orderId": order_id,
            "userId": user_id,
            **payload
        }
    }
    send_message(settings.KAFKA_TOPIC_ORDERS, event, key=str(order_id))