"""Repository layer exports for notification service.

This module exports all repository functions for easy importing.
"""

from .notification import (
    get_user_channels,
    get_channel_by_id,
    create_channel,
    update_channel,
    delete_channel,
    get_user_email,
    save_notification_history,
    get_notification_history
)

__all__ = [
    "get_user_channels",
    "get_channel_by_id",
    "create_channel",
    "update_channel",
    "delete_channel",
    "get_user_email",
    "save_notification_history",
    "get_notification_history"
]
