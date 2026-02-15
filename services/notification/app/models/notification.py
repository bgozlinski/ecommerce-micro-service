"""Database models for notification channels and history.

This module defines SQLAlchemy models for managing user notification preferences
and tracking notification delivery history.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, func
from app.core.database import Base
import enum


class NotificationChannelType(str, enum.Enum):
    """Enumeration of supported notification channel types.
    
    Attributes:
        EMAIL: Email notification channel.
        DISCORD: Discord webhook notification channel.
    """
    EMAIL = "email"
    DISCORD = "discord"


class NotificationChannel(Base):
    """User notification channel configuration.
    
    Stores user preferences for notification delivery channels (email, Discord).
    Users can have multiple channels with one marked as primary.
    
    Attributes:
        id: Primary key.
        user_id: Foreign key to user (indexed).
        channel_type: Type of notification channel (email/discord).
        address: Channel address (email address or Discord webhook URL).
        is_primary: Whether this is the user's primary channel for this type.
        is_active: Whether this channel is currently active.
        created_at: Timestamp when channel was created.
    """
    __tablename__ = "notification_channels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel_type = Column(SQLEnum(NotificationChannelType), nullable=False)
    address = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class NotificationHistory(Base):
    """Notification delivery history log.
    
    Tracks all notification attempts for audit and debugging purposes.
    Records success/failure status and error messages.
    
    Attributes:
        id: Primary key.
        user_id: Foreign key to user (indexed).
        channel_type: Type of notification channel used.
        event_type: Type of event that triggered notification.
        recipient: Recipient address (email or webhook URL).
        subject: Email subject line (optional).
        body: Notification body content (optional).
        status: Delivery status (sent/failed).
        error_message: Error details if delivery failed (optional).
        sent_at: Timestamp when notification was sent/attempted.
    """
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel_type = Column(SQLEnum(NotificationChannelType), nullable=False)
    event_type = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, nullable=False)
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)