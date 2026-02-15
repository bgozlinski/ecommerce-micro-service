"""Kafka consumer for notification-related events.

This module provides a Kafka consumer that subscribes to order, user, and product
events and routes them to appropriate handlers for sending notifications.
"""

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json
import logging
import asyncio
from typing import Optional
from app.core.config import settings
from app.events.handlers import handle_event

logger = logging.getLogger(__name__)


class KafkaConsumerSingleton:
    """Singleton Kafka consumer for notification events."""
    
    _instance: Optional[AIOKafkaConsumer] = None

    @classmethod
    async def get_instance(cls) -> AIOKafkaConsumer:
        """Get or create Kafka consumer instance.
        
        Returns:
            AIOKafkaConsumer: Singleton consumer instance.
        """
        if cls._instance is None:
            logger.info("Tworzę nową instancję Kafka Consumer")
            
            cls._instance = AIOKafkaConsumer(
                settings.KAFKA_TOPIC_ORDERS,
                settings.KAFKA_TOPIC_USERS,
                settings.KAFKA_TOPIC_PRODUCTS,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                max_poll_records=10,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            await cls._instance.start()
            
            logger.info(f"Kafka Consumer subskrybuje topiki: {settings.KAFKA_TOPIC_ORDERS}, "
                       f"{settings.KAFKA_TOPIC_USERS}, {settings.KAFKA_TOPIC_PRODUCTS}")
        
        return cls._instance

    @classmethod
    async def close(cls):
        """Close Kafka consumer and cleanup resources."""
        if cls._instance:
            logger.info("Zamykam KafkaConsumer")
            await cls._instance.stop()
            cls._instance = None
            logger.info("KafkaConsumer zamknięty")


async def start_consumer():
    """Start Kafka consumer and process messages.
    
    This function runs in a loop, consuming messages from subscribed topics
    and routing them to appropriate event handlers.
    
    Raises:
        KafkaError: If consumer encounters an error.
    """
    consumer = await KafkaConsumerSingleton.get_instance()
    
    logger.info("Kafka Consumer uruchomiony - oczekiwanie na eventy...")
    
    try:
        async for message in consumer:
            try:
                logger.info(f"Otrzymano event z topiku {message.topic} "
                           f"[partition {message.partition}] @ offset {message.offset}")
                logger.debug(f"Event payload: {message.value}")
                
                # Route event to handler
                await handle_event(message.value)
                
            except Exception as e:
                logger.error(f"Błąd przetwarzania eventu: {e}", exc_info=True)
                # Continue processing next messages even if one fails
                continue
                
    except KeyboardInterrupt:
        logger.info("Otrzymano sygnał przerwania - zatrzymywanie konsumenta")
    except KafkaError as e:
        logger.error(f"Błąd Kafka Consumer: {e}", exc_info=True)
        raise
    finally:
        await KafkaConsumerSingleton.close()


async def consume_single_message() -> Optional[dict]:
    """Consume a single message from Kafka (for testing).
    
    Returns:
        Optional[dict]: Message payload if available, None otherwise.
    """
    consumer = await KafkaConsumerSingleton.get_instance()
    
    try:
        message_batch = await consumer.getmany(timeout_ms=1000, max_records=1)
        
        for topic_partition, messages in message_batch.items():
            if messages:
                message = messages[0]
                logger.info(f"Otrzymano event z topiku {message.topic}")
                return message.value
        
        return None
        
    except KafkaError as e:
        logger.error(f"Błąd podczas pobierania wiadomości: {e}")
        return None
