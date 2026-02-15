"""Discord notification service (placeholder).

This module provides placeholder functions for Discord notifications.
Discord integration is not yet implemented - all functions return True
without performing any actual operations.
"""

import logging

logger = logging.getLogger(__name__)


async def send_discord_notification(webhook_url: str, message: str, embed: dict = None):
    """Send notification to Discord via webhook (placeholder).
    
    This is a placeholder function. Discord integration is not yet implemented.
    
    Args:
        webhook_url: Discord webhook URL (not used).
        message: Message content (not used).
        embed: Optional embed object (not used).
        
    Returns:
        bool: Always returns True (placeholder).
    """
    logger.info("Discord notification placeholder called (not implemented)")
    return True


async def send_order_paid_discord(webhook_url: str, order_id: int, user_id: int):
    """Send order paid notification to Discord (placeholder).
    
    This is a placeholder function. Discord integration is not yet implemented.
    
    Args:
        webhook_url: Discord webhook URL (not used).
        order_id: Order identifier (not used).
        user_id: User identifier (not used).
        
    Returns:
        bool: Always returns True (placeholder).
    """
    logger.info(f"Discord order paid notification placeholder: order_id={order_id}, user_id={user_id}")
    return True
