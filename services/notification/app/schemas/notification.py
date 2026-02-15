"""Pydantic schemas for notification API requests and responses.

This module defines data validation and serialization schemas for notification
channel management and notification history.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationChannelType


class NotificationChannelBase(BaseModel):
    """Base schema for notification channel."""
    channel_type: NotificationChannelType
    address: str
    is_primary: bool = False
    is_active: bool = True


class NotificationChannelCreate(NotificationChannelBase):
    """Schema for creating a new notification channel."""
    user_id: int


class NotificationChannelUpdate(BaseModel):
    """Schema for updating notification channel settings."""
    address: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class NotificationChannelResponse(NotificationChannelBase):
    """Schema for notification channel response."""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryResponse(BaseModel):
    """Schema for notification history response."""
    id: int
    user_id: int
    channel_type: NotificationChannelType
    event_type: str
    recipient: str
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
