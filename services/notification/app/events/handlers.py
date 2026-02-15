"""Event handlers for notification service.

This module contains handlers for different event types received from Kafka,
routing them to appropriate notification services (email, Discord).
"""

import logging
from typing import Dict, Any
from app.core.database import SessionLocal
from app.repositories.notification import get_user_email, save_notification_history
from app.models.notification import NotificationChannelType
from app.services.email_service import (
    send_welcome_email,
    send_order_confirmation,
    send_payment_confirmation,
    send_order_failed
)
from app.services.discord_service import send_order_paid_discord
from app.core.config import settings

logger = logging.getLogger(__name__)


async def handle_event(event: Dict[str, Any]) -> None:
    """Route event to appropriate handler based on event type.
    
    Args:
        event: Event payload containing eventType and payload fields.
    """
    event_type = event.get("eventType")
    payload = event.get("payload", {})
    
    if not event_type:
        logger.warning(f"Event bez eventType: {event}")
        return
    
    handlers = {
        "user_registered": handle_user_registered,
        "order_created": handle_order_created,
        "order_paid": handle_order_paid,
        "order_failed": handle_order_failed,
        "order_cancelled": handle_order_cancelled,
        "product_created": handle_product_created,
        "product_updated": handle_product_updated
    }
    
    handler = handlers.get(event_type)
    if handler:
        try:
            await handler(payload)
        except Exception as e:
            logger.error(f"Błąd obsługi eventu {event_type}: {e}", exc_info=True)
    else:
        logger.warning(f"Brak handlera dla eventu: {event_type}")


async def handle_user_registered(payload: Dict[str, Any]) -> None:
    """Handle user_registered event - send welcome email.
    
    Args:
        payload: Event payload containing userId and email.
    """
    user_id = payload.get("userId")
    email = payload.get("email")
    
    if not email or not user_id:
        logger.warning(f"Brak email lub userId w evencie user_registered: {payload}")
        return
    
    logger.info(f"Obsługa user_registered dla userId={user_id}, email={email}")
    
    db = SessionLocal()
    try:
        # Send welcome email
        success = await send_welcome_email(email, user_id)
        
        # Save notification history
        save_notification_history(
            db=db,
            user_id=user_id,
            channel_type=NotificationChannelType.EMAIL,
            event_type="user_registered",
            recipient=email,
            subject="Welcome to GameKeys Store!",
            status="sent" if success else "failed",
            error_message=None if success else "Failed to send email"
        )
        
        if success:
            logger.info(f"Email powitalny wysłany do {email}")
        else:
            logger.error(f"Nie udało się wysłać emaila powitalnego do {email}")
            
    except Exception as e:
        logger.error(f"Błąd podczas obsługi user_registered: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_created(payload: Dict[str, Any]) -> None:
    """Handle order_created event - send order confirmation email.
    
    Args:
        payload: Event payload containing orderId, userId, totalAmount.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")
    total_amount = payload.get("totalAmount", 0) / 100  # cents to PLN
    
    if not order_id or not user_id:
        logger.warning(f"Brak orderId lub userId w evencie order_created: {payload}")
        return
    
    logger.info(f"Obsługa order_created dla orderId={order_id}, userId={user_id}")
    
    db = SessionLocal()
    try:
        # Get user email
        email = get_user_email(db, user_id)
        if not email:
            logger.warning(f"Brak emaila dla userId={user_id}")
            return
        
        # Send order confirmation
        success = await send_order_confirmation(email, order_id, total_amount)
        
        # Save notification history
        save_notification_history(
            db=db,
            user_id=user_id,
            channel_type=NotificationChannelType.EMAIL,
            event_type="order_created",
            recipient=email,
            subject=f"Order #{order_id} Confirmation",
            status="sent" if success else "failed",
            error_message=None if success else "Failed to send email"
        )
        
        if success:
            logger.info(f"Email potwierdzenia zamówienia wysłany do {email}")
        else:
            logger.error(f"Nie udało się wysłać emaila potwierdzenia do {email}")
            
    except Exception as e:
        logger.error(f"Błąd podczas obsługi order_created: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_paid(payload: Dict[str, Any]) -> None:
    """Handle order_paid event - send payment confirmation with keys.
    
    Args:
        payload: Event payload containing orderId, userId, keys.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")
    keys = payload.get("keys", [])
    
    if not order_id or not user_id:
        logger.warning(f"Brak orderId lub userId w evencie order_paid: {payload}")
        return
    
    logger.info(f"Obsługa order_paid dla orderId={order_id}, userId={user_id}, keys={len(keys)}")
    
    db = SessionLocal()
    try:
        # Get user email
        email = get_user_email(db, user_id)
        if not email:
            logger.warning(f"Brak emaila dla userId={user_id}")
            return
        
        # Send payment confirmation with keys
        success = await send_payment_confirmation(email, order_id, keys)
        
        # Save notification history
        save_notification_history(
            db=db,
            user_id=user_id,
            channel_type=NotificationChannelType.EMAIL,
            event_type="order_paid",
            recipient=email,
            subject=f"Your Game Keys - Order #{order_id}",
            body=f"Keys: {', '.join(keys)}",
            status="sent" if success else "failed",
            error_message=None if success else "Failed to send email"
        )
        
        if success:
            logger.info(f"Email z kluczami wysłany do {email}")
        else:
            logger.error(f"Nie udało się wysłać emaila z kluczami do {email}")
        
        # Send Discord notification if configured
        if settings.DISCORD_WEBHOOK_URL:
            discord_success = await send_order_paid_discord(
                settings.DISCORD_WEBHOOK_URL, 
                order_id, 
                user_id
            )
            
            if discord_success:
                logger.info(f"Powiadomienie Discord wysłane dla orderId={order_id}")
            else:
                logger.error(f"Nie udało się wysłać powiadomienia Discord")
                
    except Exception as e:
        logger.error(f"Błąd podczas obsługi order_paid: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_failed(payload: Dict[str, Any]) -> None:
    """Handle order_failed event - send failure notification.
    
    Args:
        payload: Event payload containing orderId, userId, reason.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")
    reason = payload.get("reason", "Unknown error")
    
    if not order_id or not user_id:
        logger.warning(f"Brak orderId lub userId w evencie order_failed: {payload}")
        return
    
    logger.info(f"Obsługa order_failed dla orderId={order_id}, userId={user_id}")
    
    db = SessionLocal()
    try:
        # Get user email
        email = get_user_email(db, user_id)
        if not email:
            logger.warning(f"Brak emaila dla userId={user_id}")
            return
        
        # Send failure notification
        success = await send_order_failed(email, order_id, reason)
        
        # Save notification history
        save_notification_history(
            db=db,
            user_id=user_id,
            channel_type=NotificationChannelType.EMAIL,
            event_type="order_failed",
            recipient=email,
            subject=f"Order #{order_id} Failed",
            body=f"Reason: {reason}",
            status="sent" if success else "failed",
            error_message=None if success else "Failed to send email"
        )
        
        if success:
            logger.info(f"Email o niepowodzeniu zamówienia wysłany do {email}")
        else:
            logger.error(f"Nie udało się wysłać emaila o niepowodzeniu do {email}")
            
    except Exception as e:
        logger.error(f"Błąd podczas obsługi order_failed: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_cancelled(payload: Dict[str, Any]) -> None:
    """Handle order_cancelled event - send cancellation notification.
    
    Args:
        payload: Event payload containing orderId, userId.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")
    
    if not order_id or not user_id:
        logger.warning(f"Brak orderId lub userId w evencie order_cancelled: {payload}")
        return
    
    logger.info(f"Obsługa order_cancelled dla orderId={order_id}, userId={user_id}")
    
    # Treat cancellation similar to failure
    await handle_order_failed({
        "orderId": order_id,
        "userId": user_id,
        "reason": "Order cancelled by user or system"
    })


async def handle_product_created(payload: Dict[str, Any]) -> None:
    """Handle product_created event - currently no notification needed.
    
    Args:
        payload: Event payload containing productId, name, price.
    """
    product_id = payload.get("productId")
    logger.info(f"Otrzymano event product_created dla productId={product_id} - brak akcji")


async def handle_product_updated(payload: Dict[str, Any]) -> None:
    """Handle product_updated event - currently no notification needed.
    
    Args:
        payload: Event payload containing productId, changes.
    """
    product_id = payload.get("productId")
    logger.info(f"Otrzymano event product_updated dla productId={product_id} - brak akcji")
